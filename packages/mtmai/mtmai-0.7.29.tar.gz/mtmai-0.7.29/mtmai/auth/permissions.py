"""
权限检测系统
提供用户权限验证、组织权限检查等功能
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

# 使用标准库logging
logger = logging.getLogger(__name__)

# 简化配置，避免依赖mtmai.core.config
class Settings:
    DEFAULT_MAX_STEPS = 25

settings = Settings()


class Permission(str, Enum):
    """权限枚举"""
    # 任务相关权限
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_EXECUTE = "task:execute"

    # 组织相关权限
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_ADMIN = "org:admin"

    # 系统管理权限
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"


class Role(str, Enum):
    """角色枚举"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


@dataclass
class Organization:
    """组织模型"""
    organization_id: str
    name: str
    status: str = "active"


@dataclass
class User:
    """用户模型"""
    id: str
    username: str
    email: str
    role: Role = Role.USER
    organization_id: Optional[str] = None
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True


class PermissionChecker:
    """权限检查器"""

    def __init__(self):
        # 角色权限映射
        self.role_permissions: Dict[Role, Set[Permission]] = {
            Role.GUEST: {
                Permission.TASK_READ,
            },
            Role.USER: {
                Permission.TASK_CREATE,
                Permission.TASK_READ,
                Permission.TASK_UPDATE,
                Permission.TASK_DELETE,
                Permission.TASK_EXECUTE,
                Permission.ORG_READ,
            },
            Role.ADMIN: {
                Permission.TASK_CREATE,
                Permission.TASK_READ,
                Permission.TASK_UPDATE,
                Permission.TASK_DELETE,
                Permission.TASK_EXECUTE,
                Permission.ORG_READ,
                Permission.ORG_UPDATE,
                Permission.ORG_ADMIN,
                Permission.SYSTEM_ADMIN,
                Permission.SYSTEM_CONFIG,
            },
        }

    async def check_user_permission(
        self,
        user: User,
        permission: Permission,
        organization: Optional[Organization] = None
    ) -> bool:
        """
        检查用户是否具有指定权限

        Args:
            user: 用户对象
            permission: 要检查的权限
            organization: 组织对象（可选）

        Returns:
            是否具有权限
        """
        logger.debug(f"检查用户权限: user_id={user.id}, permission={permission}")

        # 检查用户是否激活
        if not user.is_active:
            logger.warning(f"用户未激活: user_id={user.id}")
            return False

        # 检查用户直接权限
        if permission in user.permissions:
            logger.debug(f"用户具有直接权限: user_id={user.id}, permission={permission}")
            return True

        # 检查角色权限
        role_permissions = self.role_permissions.get(user.role, set())
        if permission in role_permissions:
            logger.debug(f"用户通过角色具有权限: user_id={user.id}, role={user.role}, permission={permission}")
            return True

        # 检查组织权限
        if organization and user.organization_id == organization.organization_id:
            # 如果是组织内的权限检查，可以添加额外的逻辑
            if organization.status == "active":
                logger.debug(f"用户在活跃组织中: user_id={user.id}, org_id={organization.organization_id}")
                # 这里可以添加组织级别的权限检查逻辑

        logger.warning(f"用户权限不足: user_id={user.id}, permission={permission}")
        return False

    async def check_organization_permission(
        self,
        user: User,
        organization: Organization,
        permission: Permission
    ) -> bool:
        """
        检查用户在特定组织中的权限

        Args:
            user: 用户对象
            organization: 组织对象
            permission: 要检查的权限

        Returns:
            是否具有权限
        """
        logger.debug(f"检查组织权限: user_id={user.id}, org_id={organization.organization_id}, permission={permission}")

        # 检查用户是否属于该组织
        if user.organization_id != organization.organization_id:
            logger.warning(f"用户不属于该组织: user_id={user.id}, user_org={user.organization_id}, target_org={organization.organization_id}")
            return False

        # 检查组织状态
        if organization.status != "active":
            logger.warning(f"组织未激活: org_id={organization.organization_id}, status={organization.status}")
            return False

        # 使用通用权限检查
        return await self.check_user_permission(user, permission, organization)

    async def get_user_permissions(self, user: User) -> Set[Permission]:
        """
        获取用户的所有权限

        Args:
            user: 用户对象

        Returns:
            用户权限集合
        """
        permissions = set(user.permissions)

        # 添加角色权限
        role_permissions = self.role_permissions.get(user.role, set())
        permissions.update(role_permissions)

        logger.debug(f"用户权限列表: user_id={user.id}, permissions={permissions}")
        return permissions

    def has_admin_permission(self, user: User) -> bool:
        """
        检查用户是否具有管理员权限

        Args:
            user: 用户对象

        Returns:
            是否为管理员
        """
        return user.role == Role.ADMIN


class PermissionCheckerFactory:
    """权限检查器工厂类"""

    _instance: Optional[PermissionChecker] = None

    @classmethod
    def get_instance(cls) -> PermissionChecker:
        """
        获取权限检查器实例（单例模式）

        Returns:
            PermissionChecker实例
        """
        if cls._instance is None:
            cls._instance = PermissionChecker()
            logger.info("创建新的PermissionChecker实例")
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """重置权限检查器实例（主要用于测试）"""
        cls._instance = None
        logger.info("重置PermissionChecker实例")


# 权限装饰器
def require_permission(permission: Permission):
    """
    权限检查装饰器

    Args:
        permission: 需要的权限
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以从请求上下文中获取用户信息
            # 实际实现时需要根据具体的认证系统来获取用户
            logger.debug(f"权限检查装饰器: 需要权限 {permission}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 便捷函数
async def check_task_permission(user: User, action: str) -> bool:
    """
    检查任务相关权限的便捷函数

    Args:
        user: 用户对象
        action: 操作类型 (create, read, update, delete, execute)

    Returns:
        是否具有权限
    """
    permission_map = {
        "create": Permission.TASK_CREATE,
        "read": Permission.TASK_READ,
        "update": Permission.TASK_UPDATE,
        "delete": Permission.TASK_DELETE,
        "execute": Permission.TASK_EXECUTE,
    }

    permission = permission_map.get(action)
    if not permission:
        logger.error(f"未知的任务操作: {action}")
        return False

    checker = PermissionCheckerFactory.get_instance()
    return await checker.check_user_permission(user, permission)
