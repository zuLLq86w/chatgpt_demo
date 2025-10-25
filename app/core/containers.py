from dependency_injector import containers, providers

from app import api
from app.repositories import *
from app.services import *
from .config import settings
from .db import Database
# from .redisclient import RedisPool


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[api])

    db = providers.Singleton(
        Database,
        db_url=settings.SQLALCHEMY_DATABASE_URI,
    )

    # redis_pool = providers.Singleton(RedisPool, url=settings.REDIS_URI)

    # region 注入repository依赖

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )
    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )

    conversation_repository = providers.Factory(
        ConversationRepository,
        session_factory=db.provided.session,
    )

    conversation_tag_rel_repository = providers.Factory(
        ConversationTagRelRepository,
        session_factory=db.provided.session,
    )

    tag_repository = providers.Factory(
        TagRepository,
        session_factory=db.provided.session,
    )
    tag_service = providers.Factory(
        TagService,
        repository=tag_repository,
    )

    message_repository = providers.Factory(
        MessageRepository,
        session_factory=db.provided.session,
    )

    group_repository = providers.Factory(
        GroupRepository,
        session_factory=db.provided.session,
    )

    group_robot_repository = providers.Factory(
        GroupRobotRepository,
        session_factory=db.provided.session,
    )

    group_member_repository = providers.Factory(
        GroupMemberRepository,
        session_factory=db.provided.session,
    )

    group_robot_rel_repository = providers.Factory(
        GroupRobotRelRepository,
        session_factory=db.provided.session,
    )

    # 注入service依赖
    conversation_service = providers.Factory(
        ConversationService,
        repository=conversation_repository,
        con_tag_rel_repo=conversation_tag_rel_repository,
        message_repo=message_repository,
        user_repo=user_repository,
    )

    group_service = providers.Factory(
        GroupService,
        repository=group_repository,
        robot_repo=group_robot_repository,
        group_member_repo=group_member_repository,
        group_robot_rel_repo=group_robot_rel_repository,
        conversation_repo=conversation_repository,
        user_repo=user_repository,
        message_repo=message_repository,
    )


