from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi_utils.cbv import cbv
from dependency_injector.wiring import Provide, inject
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreateIn, UserOut, TokenOut, LoginIn
from app.services.users import UserService
from app.core.containers import Container

router = APIRouter(tags=["users"])

@cbv(router)
class UsersCBV:

    @inject
    def __init__(
        self,
        user_services: UserService = Depends(Provide[Container.user_service]),
    ):
        self.user_services = user_services

    @router.post("/register", summary="登陆", response_model=UserOut)
    async def register(self, body: UserCreateIn):
        return await self.user_services.register(body)

    @router.post("/login", summary="注册", response_model=TokenOut)
    async def login(self, body: Annotated[OAuth2PasswordRequestForm, Depends()]):
        return await self.user_services.login(body.username, body.password)

