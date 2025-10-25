import datetime
import uuid

from app.models import User
from app.repositories import UserRepository
from app.schemas.user import UserCreateIn, TokenOut
from app.core.auth import get_password_hash, verify_password, create_access_token
from app.core.exceptions import HTTPBadRequest


class UserService:

    def __init__(self, repository: UserRepository) -> None:
        self._repository: UserRepository = repository

    async def register(self, user: UserCreateIn) -> User:
        # check username
        is_exist = await self._repository.is_exist_by_username(user.username)
        if is_exist:
            raise HTTPBadRequest("username already exists")

        user.password = get_password_hash(user.password)
        id = str(uuid.uuid4())
        user = User(id=id, create_date=datetime.datetime.now(datetime.UTC), **user.dict())
        await self._repository.create(user)
        return await self._repository.get_by_id(id)

    async def login(self, username: str, password: str) -> TokenOut:
        user = await self._repository.get_by_username(username)
        if not user:
            raise HTTPBadRequest("User not found")

        if not verify_password(password, user.password):
            raise HTTPBadRequest("Invalid password")

        token = create_access_token(user.id)
        # TODO: 存储在redis中，登陆时需要检验
        return TokenOut(access_token=token)
