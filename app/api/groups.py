import json

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List
from fastapi_utils.cbv import cbv
from dependency_injector.wiring import Provide, inject

from app.api.deps import get_current_user
from app.schemas import RobotCreateIn, GroupCreateIn, CurrentUser, DefaultPageResponse, GroupOut, GroupDetailOut, \
    GroupMsgIn, GroupMsgOut, DefaultPageParams
from app.services import GroupService
from app.core.containers import Container

router = APIRouter(tags=["groups"])

@cbv(router)
class GroupsCBV:

    @inject
    def __init__(
        self,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        group_service: GroupService = Depends(Provide[Container.group_service]),
    ):
        self.current_user = current_user
        self.group_service = group_service

    @router.post("/groups/robot", summary="新建机器人")
    async def create_group_robot(self, body: RobotCreateIn):
        await self.group_service.create_robot(name=body.name, personality=body.personality, keywords=json.dumps(body.keywords, ensure_ascii=False))

    @router.post("/groups", summary="新建群组")
    async def register(self, body: GroupCreateIn):
        await self.group_service.create_group(title=body.title, user_id=self.current_user.id, robot_ids=body.robot_ids, member_user_ids=body.member_user_ids)

    @router.get("/groups", summary="获取群组", response_model=DefaultPageResponse[GroupOut])
    async def get_groups(self):
        data = await self.group_service.get_list(self.current_user.id)
        return DefaultPageResponse[GroupOut](total=len(data), data=data)

    @router.get("/groups/{group_id}", summary="获取群组详情", response_model=GroupDetailOut)
    async def get_group_detail(self, group_id: str):
        return await self.group_service.get_detail(group_id)

    @router.post("/groups/{group_id}/message", summary="发送群组消息", response_model=List[GroupMsgOut])
    async def send_group_message(self, group_id: str, body: GroupMsgIn):
        return await self.group_service.send_group_message(group_id, self.current_user.id, body.content)

    @router.get("/groups/{group_id}/message", summary="查看群组消息记录", response_model=DefaultPageResponse[GroupMsgOut])
    async def get_group_message(self, group_id: str, params: Annotated[DefaultPageParams, Depends()]):
        total, data = await self.group_service.get_group_msg(group_id, self.current_user.id, params.limit, params.offset)
        return DefaultPageResponse[GroupMsgOut](total=total, data=data)
