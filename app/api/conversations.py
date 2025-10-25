from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi.responses import StreamingResponse
from dependency_injector.wiring import Provide, inject
from typing import Annotated

from app.schemas import ConversationCreateOut, ConversationCreateIn, CurrentUser, DefaultPageResponse, ConversationOut, DefaultPageParams, TagCreateIn, TagCreateOut, TagOut, ConversationUpdateIn, PersonalMsgIn, ConversationMessageOut, PersonalConversationPageParams
from app.services import ConversationService, TagService
from app.core.containers import Container
from .deps import get_current_user

router = APIRouter(tags=["会话"])


@cbv(router)
class ConversationCBV:

    @inject
    def __init__(
        self,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        conversation_services: ConversationService = Depends(Provide[Container.conversation_service]),
        tag_service: TagService = Depends(Provide[Container.tag_service]),
    ):
        self.current_user = current_user
        self.conversation_services = conversation_services
        self.tag_service = tag_service

    @router.post("/conversations", summary="创建会话", response_model=ConversationCreateOut)
    async def create_conversation(self, body: ConversationCreateIn):
        return await self.conversation_services.create(title=body.title, user_id=self.current_user.id, is_group=False, group_id=None, tag_ids=body.tag_ids)

    @router.get("/conversations", summary="获取用户所有个人会话", response_model=DefaultPageResponse[ConversationOut])
    async def get_user_conversations(
        self,
        params: Annotated[PersonalConversationPageParams, Depends()]
    ):
        return await self.conversation_services.get_user_conversations(self.current_user.id, params)

    @router.put("/conversations/{id}", summary="修改个人会话")
    async def update_conversation(self, id: str, body: ConversationUpdateIn):
        await self.conversation_services.update_user_conversation(id, self.current_user.id, body.title)

    @router.delete("/conversations/{id}", summary="删除会话")
    async def delete_conversation(self, id: str):
        await self.conversation_services.delete_user_conversation(id, self.current_user.id)

    @router.get(
        "/{conversation_id}/messages",
        summary="查看会话消息",
        response_model=DefaultPageResponse[ConversationMessageOut]
    )
    async def get_conversation_messages(
        self,
        conversation_id,
        params: Annotated[DefaultPageParams, Depends()]
    ):
        total, data = await self.conversation_services.get_messages(con_id=conversation_id, user_id=self.current_user.id, limit=params.limit, offset=params.offset)
        return DefaultPageResponse[ConversationMessageOut](data=data, total=total)

    @router.post("/{conversation_id}/messages", summary="会话发送新的消息")
    async def post_conversation_message(self, conversation_id: str, body: PersonalMsgIn):
        async def event_generator():
            async for chunk in self.conversation_services.send_personal_msg(user_id=self.current_user.id, con_id=conversation_id, content=body.content):
                yield chunk
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @router.post("/tags", summary="创建标签", response_model=TagCreateOut)
    async def create_tag(self, body: TagCreateIn):
        return await self.tag_service.create(name=body.name, user_id=self.current_user.id)

    @router.delete("/tags/{tag_id}", summary="删除标签")
    async def delete_tag(self, tag_id: str):
        await self.tag_service.delete(tag_id=tag_id, user_id=self.current_user.id)

    @router.get("/users/tags", summary="获取当前用户下的所有标签", response_model=DefaultPageResponse[TagOut])
    async def get_user_tags(self):
        data = await self.tag_service.get_user_tags(user_id=self.current_user.id)
        return DefaultPageResponse[TagOut](data=data, total=len(data))


