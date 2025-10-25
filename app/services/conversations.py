import datetime
import json
import uuid
from typing import List, AsyncGenerator, Tuple
from loguru import logger
from openai import OpenAI
from app.models import Conversation, ConversationTagRel, Message, MessageType, MessageStatus
from app.repositories import ConversationRepository, ConversationTagRelRepository, MessageRepository, UserRepository
from app.core.exceptions import HTTPBadRequest
from app.schemas import ConversationCreateIn, ConversationCreateOut, DefaultPageResponse, ConversationOut, DefaultPageParams, PersonalConversationPageParams
from app.tools.ai_client import create_completions_with_retry


class ConversationService:

    def __init__(
        self,
        repository: ConversationRepository,
        con_tag_rel_repo: ConversationTagRelRepository,
        message_repo: MessageRepository,
        user_repo: UserRepository,
    ) -> None:
        self._repository: ConversationRepository = repository
        self.con_tag_rel_repo: ConversationTagRelRepository = con_tag_rel_repo
        self.message_repo: MessageRepository = message_repo
        self.user_repo: UserRepository = user_repo

    async def create(self, title, user_id, is_group, group_id, tag_ids) -> ConversationCreateOut:
        con_id = str(uuid.uuid4())
        conversation = Conversation(id=con_id, title=title, user_id=user_id, is_group=is_group,group_id=group_id,create_date=datetime.datetime.now(datetime.UTC))
        await self._repository.create(conversation)
        for tag_id in tag_ids:
            await self.con_tag_rel_repo.create(ConversationTagRel(id=str(uuid.uuid4()), tag_id=tag_id, conversation_id=con_id))
        result = await self._repository.get_by_id(con_id)
        return ConversationCreateOut(**result.to_dict())

    async def get_user_conversations(self, user_id: str, params: PersonalConversationPageParams) -> DefaultPageResponse[ConversationOut]:
        total, data = await self._repository.get_by_user(user_id, limit=params.limit, offset=params.offset, tag_ids=params.tag_ids.split(','))

        return DefaultPageResponse[ConversationOut](total=total, data=data)

    async def update_user_conversation(self, id: str, user_id: str, title: str):
        check = await self._repository.filter_by(id=id, user_id=user_id, is_group=False)
        if len(check) == 0:
            raise HTTPBadRequest("resource not found")
        await self._repository.update(id, {"title": title})

    async def send_personal_msg(self, user_id, con_id: str, content: str) -> AsyncGenerator[str, None]:
        # 获取最近9条消息作为上下文
        contents = await self.message_repo.get_content_by_con_id(con_id)
        contents = [json.loads(i) for i in contents]

        # get user.name
        user = await self.user_repo.get_by_id(user_id)

        # 保存用户消息记录
        msg_id = str(uuid.uuid4())
        await self.message_repo.create(Message(id=msg_id, conversation_id=con_id, type=MessageType.user.value, name=user.name, content=json.dumps({"role": "user", "content": content}, ensure_ascii=False), data=None, status=MessageStatus.ok.value, create_date=datetime.datetime.now(datetime.UTC)))

        contents.append({"role": "user", "content": content})

        ai_content = ""
        ai_msg_id = str(uuid.uuid4())
        await self.message_repo.create(
            Message(
                id=ai_msg_id,
                conversation_id=con_id,
                type=MessageType.system.value,
                name="system",
                content=json.dumps({"role": "assistant", "content": ""}, ensure_ascii=False),
                data=None,
                status=MessageStatus.pending.value,
                create_date=datetime.datetime.now(datetime.UTC)
            )
        )

        try:
            response = await create_completions_with_retry(messages=contents, max_retry=2)
            for stream in response:
                delta = stream.choices[0].delta.content or ""
                if delta:
                    ai_content += delta
                    yield delta

        except Exception as e:
            error_msg = str(e)
            logger.error(f"AI生成失败: {error_msg}")
            await self.message_repo.update(
                ai_msg_id,
                {
                    "content": json.dumps(
                        {
                            "role": "assistant",
                            "content": ai_content
                        }, ensure_ascii=False),
                    "status": MessageStatus.error.value,
                    "data": json.dumps({"error": error_msg}, ensure_ascii=False)
                }
            )
            yield f"[ERROR] {error_msg}"
        else:
            await self.message_repo.update(
                ai_msg_id,
                {
                    "content": json.dumps(
                        {
                            "role": "assistant",
                            "content": ai_content
                        }, ensure_ascii=False),
                    "status": MessageStatus.ok.value
                })
        # 返回结果
        yield "[DONE]"

    async def get_messages(self, con_id: str, user_id: str, limit: int = 10, offset: int = 0) -> Tuple[int, List[Message]]:
        check = await self._repository.filter_by(id=con_id, user_id=user_id, is_group=False)
        if len(check) == 0:
            raise HTTPBadRequest("resource not found")

        total, data = await self.message_repo.get_messages_by_con_id(con_id, limit, offset)
        return total, data

    async def delete_user_conversation(self, con_id: str, user_id: str):
        check = await self._repository.filter_by(id=con_id, user_id=user_id, is_group=False)
        if len(check) == 0:
            raise HTTPBadRequest("resource not found")

        await self._repository.delete(con_id)