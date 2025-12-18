import logging
from contextvars import ContextVar
from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from mtmai.core.auth import TokenDecodeError, decode_token
from mtmai.core.config import settings

# from mtmai.db.db_manager import DatabaseManager
from mtmai.models.models import User
from mtmai.models.tenant import Tenant
from mtmai.models.user import TenantMember
from google.adk.sessions.base_session_service import BaseSessionService


logger = logging.getLogger(__name__)

user_context: ContextVar[User | None] = ContextVar("user", default=None)


# DATABASE_URL = "postgresql+asyncpg://user:password@host/database"
async_engine: Optional[AsyncEngine] = None


def get_async_engine():
    global async_engine
    if not async_engine:
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        db_url = settings.MTM_DATABASE_URL
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        async_engine = create_async_engine(db_url)
    return async_engine


# Global manager instances
# _db_manager: Optional[DatabaseManager] = None


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/login/access-token",
    auto_error=False,  # 没有 token header 时不触发异常
)


def get_user() -> User | None:
    return user_context.get()


# async def get_db() -> DatabaseManager:
#     """Dependency provider for database manager"""
#     if not _db_manager:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Database manager not initialized",
#         )
#     return _db_manager


# async def get_websocket_manager() -> WebSocketManager:
#     """Dependency provider for connection manager"""
#     if not _websocket_manager:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Connection manager not initialized",
#         )
#     return _websocket_manager


# async def get_team_manager() -> TeamManager:
#     """Dependency provider for team manager"""
#     if not _team_manager:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Team manager not initialized",
#         )
#     return _team_manager


# Authentication dependency functions will be defined after the dependency annotations


# Manager initialization and cleanup
async def init_managers(database_uri: str, config_dir: str, app_root: str) -> None:
    """Initialize all manager instances"""
    global _db_manager, _websocket_manager, _team_manager

    logger.info("Initializing managers...")

    try:
        pass
        # Initialize database manager
        # _db_manager = DatabaseManager(engine_uri=database_uri, base_dir=app_root)
        # _db_manager.initialize_database(auto_upgrade=settings.UPGRADE_DATABASE)

        # # init default team config
        # await _db_manager.import_teams_from_directory(
        #     config_dir, settings.DEFAULT_USER_ID, check_exists=True
        # )

        # Initialize connection manager
        # _websocket_manager = WebSocketManager(db_manager=_db_manager)
        # logger.info("Connection manager initialized")

        # Initialize team manager
        # _team_manager = TeamManager()
        # logger.info("Team manager initialized")

    except Exception as e:
        logger.error(f"Failed to initialize managers: {str(e)}")
        await cleanup_managers()  # Cleanup any partially initialized managers
        raise


# async def cleanup_managers() -> None:
#     """Cleanup and shutdown all manager instances"""
#     global _db_manager, _websocket_manager, _team_manager

#     logger.info("Cleaning up managers...")

#     # Cleanup connection manager first to ensure all active connections are closed
#     if _websocket_manager:
#         try:
#             await _websocket_manager.cleanup()
#         except Exception as e:
#             logger.error(f"Error cleaning up connection manager: {str(e)}")
#         finally:
#             _websocket_manager = None

#     # TeamManager doesn't need explicit cleanup since WebSocketManager handles it
#     _team_manager = None

#     # Cleanup database manager last
#     if _db_manager:
#         try:
#             await _db_manager.close()
#         except Exception as e:
#             logger.error(f"Error cleaning up database manager: {str(e)}")
#         finally:
#             _db_manager = None

#     logger.info("All managers cleaned up")


# Utility functions for dependency management
def get_manager_status() -> dict:
    """Get the initialization status of all managers"""
    return {
        "database_manager": _db_manager is not None,
        "websocket_manager": _websocket_manager is not None,
        "team_manager": _team_manager is not None,
    }


# Combined dependencies
async def get_managers():
    """Get all managers in one dependency"""
    return {
        "db": await get_db(),
        # "connection": await get_websocket_manager(),
        # "team": await get_team_manager(),
    }


# Error handling for manager operations
class ManagerOperationError(Exception):
    """Custom exception for manager operation errors"""

    def __init__(self, manager_name: str, operation: str, detail: str):
        self.manager_name = manager_name
        self.operation = operation
        self.detail = detail
        super().__init__(f"{manager_name} failed during {operation}: {detail}")


# Dependency for requiring specific managers
def require_managers(*manager_names: str):
    """Decorator to require specific managers for a route"""

    async def dependency():
        status = get_manager_status()
        missing = [name for name in manager_names if not status.get(f"{name}_manager")]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Required managers not available: {', '.join(missing)}",
            )
        return True

    return Depends(dependency)


async def get_asession() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(get_async_engine()) as session:
        yield session


# async def get_async_session() -> AsyncSession:
#         async with AsyncSession(engine) as session:
#             yield session


# SessionDep = Annotated[AsyncSession, Depends(get_db)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_asession)]
TokenDep = Annotated[str | None, Depends(reusable_oauth2)]


def get_host_from_request(request: Request):
    host = request.headers.get("Host")
    return host


HostDep = Annotated[str, Depends(get_host_from_request)]


# Authentication dependency functions
async def get_current_user(session: AsyncSessionDep, token: TokenDep) -> User:
    """
    Dependency for getting the current authenticated user.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
        user_id = payload.sub
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except TokenDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail,
        )

    # 查询用户
    stmt = select(User).where(User.id == user_id)
    result = await session.exec(stmt)
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user


async def get_current_tenant(
    session: AsyncSessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    request: Request,
) -> Tenant:
    """
    Dependency for getting the current tenant based on the authenticated user.
    This implements the multi-tenant architecture where users can belong to multiple tenants.
    """
    # 从请求头中获取租户ID（可选）
    tenant_id_header = request.headers.get("X-Tenant-ID")

    if tenant_id_header:
        # 如果请求头中指定了租户ID，验证用户是否属于该租户
        # 查询TenantMember表来验证用户和租户的关系
        member_stmt = select(TenantMember).where(
            and_(
                TenantMember.tenant_id == tenant_id_header,
                TenantMember.user_id == current_user.id,
                TenantMember.deleted_at == None,
            )
        )
        member_result = await session.exec(member_stmt)
        member = member_result.first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to the specified tenant",
            )

        # 获取租户信息
        stmt = select(Tenant).where(Tenant.id == tenant_id_header)
        result = await session.exec(stmt)
        tenant = result.first()

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
            )

        return tenant

    # 如果没有指定租户ID，返回用户的默认租户
    # 查询用户关联的第一个租户
    member_stmt = (
        select(TenantMember)
        .where(
            and_(
                TenantMember.user_id == current_user.id, TenantMember.deleted_at == None
            )
        )
        .limit(1)
    )
    member_result = await session.exec(member_stmt)
    member = member_result.first()

    if member:
        # 获取租户信息
        stmt = select(Tenant).where(Tenant.id == member.tenant_id)
        result = await session.exec(stmt)
        tenant = result.first()
        if tenant:
            return tenant

    # 如果用户没有关联任何租户，创建一个默认租户并关联用户
    default_tenant = Tenant(
        name="Default Tenant",
        slug="default",
        analytics_opt_out=False,
        alert_member_emails=True,
    )
    session.add(default_tenant)
    await session.commit()
    await session.refresh(default_tenant)

    # 创建租户成员关系
    tenant_member = TenantMember(
        tenant_id=default_tenant.id, user_id=current_user.id, role="admin"
    )
    session.add(tenant_member)
    await session.commit()

    return default_tenant


# 新的认证依赖
CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentTenantDep = Annotated[Tenant, Depends(get_current_tenant)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_optional_current_user(
    session: AsyncSessionDep, token: TokenDep, request: Request
) -> User | None:
    token = token or request.cookies.get(settings.COOKIE_ACCESS_TOKEN)
    if not token:
        return None
    try:
        return get_current_user(session, token, request)
    except HTTPException:
        return None


OptionalUserDep = Annotated[User | None, Depends(get_optional_current_user)]


# 配置API Session Service
def get_session_service():
    from mtmai.adk.session_service import MtAdkSessionService
    from mtmai.core.config import settings

    # 使用环境变量或配置获取mtgate API URL
    # api_base_url = getattr(settings, "MTGATE_API_URL", "https://mtgate.yuepa8.com")
    # TODO: 从当前用户上下文获取access_token
    access_token = None
    return MtAdkSessionService(base_url="", access_token=access_token)


AdkSessionDep = Annotated[BaseSessionService, Depends(get_session_service)]
