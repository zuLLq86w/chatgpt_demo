from fastapi import APIRouter
from . import users
from . import conversations
from . import groups

api_router = APIRouter(prefix="/api")
api_router.include_router(users.router)
api_router.include_router(conversations.router)
api_router.include_router(groups.router)

__all__ = ["api_router"]


