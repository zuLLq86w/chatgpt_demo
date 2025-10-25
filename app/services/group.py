import datetime
import random
import uuid
import json
from typing import List, Optional, Dict, Tuple

from app.models import Group, GroupRobot, GroupMember, GroupRobotRel, Conversation, Message, MessageType, MessageStatus
from app.repositories import GroupRepository, GroupRobotRepository, GroupMemberRepository, GroupRobotRelRepository, \
    ConversationRepository, UserRepository, MessageRepository
from app.core.exceptions import HTTPBadRequest
from app.schemas import GroupDetailOut, GroupSettings
from loguru import logger

from app.tools.ai_client import create_completions_with_retry


class GroupService:

    def __init__(
        self,
        repository: GroupRepository,
        robot_repo: GroupRobotRepository,
        group_member_repo: GroupMemberRepository,
        group_robot_rel_repo: GroupRobotRelRepository,
        conversation_repo: ConversationRepository,
        user_repo: UserRepository,
        message_repo: MessageRepository,
    ) -> None:
        self._repository: GroupRepository = repository
        self._robot_repo: GroupRobotRepository = robot_repo
        self._group_member_repo: GroupMemberRepository = group_member_repo
        self._group_robot_rel_repo: GroupRobotRelRepository = group_robot_rel_repo
        self._conversation_repo: ConversationRepository = conversation_repo
        self._user_repo: UserRepository = user_repo
        self._message_repo: MessageRepository = message_repo

    async def create_robot(self, name: str, personality: str, keywords: str) -> None:
        obj = GroupRobot(id=str(uuid.uuid4()), name=name, personality=personality, keywords=keywords)
        await self._robot_repo.create(obj)

    async def create_group(self, title: str, user_id: str, robot_ids: List[str], member_user_ids: List[str]) -> None:
        utc_now = datetime.datetime.now(datetime.UTC)
        group_id = str(uuid.uuid4())
        await self._repository.create(Group(id=group_id, create_id=user_id, create_date=utc_now, title=title))

        members = []
        members.append(GroupMember(id=str(uuid.uuid4()), group_id=group_id, user_id=user_id, is_admin=True, joined_date=utc_now))

        for i in member_user_ids:
            members.append(GroupMember(id=str(uuid.uuid4()), group_id=group_id, user_id=i, is_admin=False,joined_date=utc_now))
        await self._group_member_repo.create(members)

        rel = []
        for i in range(len(robot_ids)):
            rel.append(GroupRobotRel(
                id=str(uuid.uuid4()),
                group_id=group_id,
                robot_id=robot_ids[i],
                weight=len(robot_ids) - i
            ))
        await self._group_robot_rel_repo.create(rel)

        await self._conversation_repo.create(Conversation(
            id=str(uuid.uuid4()),
            title=title,
            is_group=True,
            create_date=utc_now,
            group_id=group_id
        ))

    async def get_list(self, user_id: str) -> List[Group]:
        return await self._repository.get_list(user_id)

    async def get_detail(self, group_id: str) -> Optional[Dict]:
        data = await self._repository.get_detail(group_id)
        if data is None:
            return None
        members = [
            {
                "id": member.user.id,
                "name": member.user.name,
                "is_admin": member.is_admin,
                "joined_date": member.joined_date,
            }
            for member in data.members
            if member.user is not None
        ]

        robots = [
            {
                "id": robot.robot.id,
                "name": robot.robot.name,
            }
            for robot in data.robots
            if robot.robot is not None
        ]

        return {
            "id": data.id,
            "title": data.title,
            "members": members,
            "robots": robots,
        }

    async def send_group_message(self, group_id: str, user_id: str, content: str):
        # 校验群组是否存在
        group_obj = await self._repository.get_by_id(group_id)
        if not group_obj:
            raise HTTPBadRequest('group not found')

        # 校验是否是群成员
        check = await self._group_member_repo.filter_by(group_id=group_id, user_id=user_id)
        if len(check) == 0:
            raise HTTPBadRequest('not a group member')

        # 获取会话id
        rows = await self._conversation_repo.filter_by(group_id=group_id)
        if len(rows) == 0:
            raise HTTPBadRequest('conversation not found')
        con_id = rows[0].id

        contents = []

        # get user.name
        user = await self._user_repo.get_by_id(user_id)

        # 保存用户消息记录
        msg_id = str(uuid.uuid4())
        await self._message_repo.create(
            Message(id=msg_id, conversation_id=con_id, type=MessageType.user.value, name=user.name,
                    content=json.dumps({"role": "user", "content": content}, ensure_ascii=False), data=None,
                    status=MessageStatus.pending.value, create_date=datetime.datetime.now(datetime.UTC)))

        contents.append({"role": "user", "content": content})


        robots = await self._robot_repo.get_robots_by_group_id(group_id)
        reponses = []
        group_settings = GroupSettings(**group_obj.settings)
        if group_settings.reponse_strategy == "all":
            for bot in robots:
                response = await create_completions_with_retry(messages=contents, max_retry=2, stream=False)
                reponses.append({
                    "type": "robot",
                    "name": bot["name"],
                    "content": response.choices[0].message.content
                })
        elif group_settings.reponse_strategy == "random":
            bot = random.choice(robots)
            response = await create_completions_with_retry(messages=contents, max_retry=2, stream=False)
            reponses.append({
                "type": "robot",
                "name": bot["name"],
                "content": response.choices[0].message.content
            })
        elif group_settings.reponse_strategy == "keyword":
            # TODO: 根据关键字匹配
            for bot in robots:
                keywords = json.loads(bot["keywords"])
                if any(keyword in content for keyword in keywords):
                    response = await create_completions_with_retry(messages=contents, max_retry=2, stream=False)
                    reponses.append({
                        "type": "robot",
                        "name": bot["name"],
                        "content": response.choices[0].message.content
                    })

        if not reponses:
            reponses.append({
                "type": "system",
                "name": "system",
                "content": "稍后回复"
            })

        for item in reponses:
            ai_msg_id = str(uuid.uuid4())
            await self._message_repo.create(
                Message(
                    id=ai_msg_id,
                    conversation_id=con_id,
                    type=MessageType(item["type"]).value,
                    name=item["name"],
                    content=json.dumps({"role": "assistant", "content": item["content"]}, ensure_ascii=False),
                    data=None,
                    status=MessageStatus.ok.value,
                    create_date=datetime.datetime.now(datetime.UTC)
                )
            )

        return reponses

    async def get_group_msg(self, group_id: str, user_id: str, limit: int, offset: int) -> Tuple[int, List[Message]]:
        # 校验群组是否存在
        group_obj = await self._repository.get_by_id(group_id)
        if not group_obj:
            raise HTTPBadRequest('group not found')

        # 校验是否是群成员
        check = await self._group_member_repo.filter_by(group_id=group_id, user_id=user_id)
        if len(check) == 0:
            raise HTTPBadRequest('not a group member')

        # 获取会话id
        rows = await self._conversation_repo.filter_by(group_id=group_id)
        if len(rows) == 0:
            raise HTTPBadRequest('conversation not found')
        con_id = rows[0].id

        total, data = await self._message_repo.get_messages_by_con_id(con_id, limit, offset)
        return total, data
