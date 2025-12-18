"""
权限系统测试用例
测试权限检测、角色权限、组织权限等功能
"""

import pytest
from mtmai.auth.permissions import (
    PermissionChecker,
    PermissionCheckerFactory,
    Permission,
    Role,
    User,
    Organization,
    check_task_permission
)


class TestPermissionChecker:
    """权限检查器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 重置单例实例
        PermissionCheckerFactory.reset_instance()
        self.checker = PermissionCheckerFactory.get_instance()

    @pytest.mark.asyncio
    async def test_user_direct_permission(self):
        """测试用户直接权限"""
        user = User(
            id="user1",
            username="testuser",
            email="test@example.com",
            role=Role.USER,
            permissions={Permission.TASK_CREATE}
        )

        # 用户具有直接权限
        assert await self.checker.check_user_permission(user, Permission.TASK_CREATE)

        # 用户没有的权限
        assert not await self.checker.check_user_permission(user, Permission.SYSTEM_ADMIN)

    @pytest.mark.asyncio
    async def test_role_based_permission(self):
        """测试基于角色的权限"""
        # 普通用户
        user = User(
            id="user2",
            username="normaluser",
            email="normal@example.com",
            role=Role.USER
        )

        # 用户角色应该具有的权限
        assert await self.checker.check_user_permission(user, Permission.TASK_CREATE)
        assert await self.checker.check_user_permission(user, Permission.TASK_READ)
        assert await self.checker.check_user_permission(user, Permission.TASK_EXECUTE)

        # 用户角色不应该具有的权限
        assert not await self.checker.check_user_permission(user, Permission.SYSTEM_ADMIN)
        assert not await self.checker.check_user_permission(user, Permission.ORG_ADMIN)

    @pytest.mark.asyncio
    async def test_admin_permission(self):
        """测试管理员权限"""
        admin_user = User(
            id="admin1",
            username="admin",
            email="admin@example.com",
            role=Role.ADMIN
        )

        # 管理员应该具有的权限
        assert await self.checker.check_user_permission(admin_user, Permission.TASK_CREATE)
        assert await self.checker.check_user_permission(admin_user, Permission.ORG_ADMIN)
        assert await self.checker.check_user_permission(admin_user, Permission.SYSTEM_ADMIN)



    @pytest.mark.asyncio
    async def test_inactive_user_permission(self):
        """测试未激活用户权限"""
        inactive_user = User(
            id="inactive1",
            username="inactive",
            email="inactive@example.com",
            role=Role.USER,
            is_active=False
        )

        # 未激活用户不应该具有任何权限
        assert not await self.checker.check_user_permission(inactive_user, Permission.TASK_READ)
        assert not await self.checker.check_user_permission(inactive_user, Permission.TASK_CREATE)

    @pytest.mark.asyncio
    async def test_organization_permission(self):
        """测试组织权限"""
        org = Organization(
            organization_id="org1",
            name="Test Organization",
            status="active"
        )

        user = User(
            id="user3",
            username="orguser",
            email="orguser@example.com",
            role=Role.USER,
            organization_id="org1"
        )

        # 用户在组织中应该具有权限
        assert await self.checker.check_organization_permission(
            user, org, Permission.TASK_CREATE
        )

        # 用户不在组织中
        other_user = User(
            id="user4",
            username="otheruser",
            email="other@example.com",
            role=Role.USER,
            organization_id="org2"
        )

        assert not await self.checker.check_organization_permission(
            other_user, org, Permission.TASK_CREATE
        )

    @pytest.mark.asyncio
    async def test_inactive_organization_permission(self):
        """测试未激活组织权限"""
        inactive_org = Organization(
            organization_id="org2",
            name="Inactive Organization",
            status="inactive"
        )

        user = User(
            id="user5",
            username="orguser2",
            email="orguser2@example.com",
            role=Role.USER,
            organization_id="org2"
        )

        # 未激活组织中的用户不应该具有权限
        assert not await self.checker.check_organization_permission(
            user, inactive_org, Permission.TASK_CREATE
        )

    @pytest.mark.asyncio
    async def test_get_user_permissions(self):
        """测试获取用户权限列表"""
        user = User(
            id="user6",
            username="testuser2",
            email="test2@example.com",
            role=Role.USER,
            permissions={Permission.SYSTEM_CONFIG}  # 额外的直接权限
        )

        permissions = await self.checker.get_user_permissions(user)

        # 应该包含角色权限和直接权限
        assert Permission.TASK_CREATE in permissions  # 角色权限
        assert Permission.SYSTEM_CONFIG in permissions  # 直接权限
        assert Permission.SYSTEM_ADMIN not in permissions  # 不应该有的权限

    def test_has_admin_permission(self):
        """测试管理员权限检查"""
        user = User(id="u1", username="user", email="user@example.com", role=Role.USER)
        admin = User(id="a1", username="admin", email="admin@example.com", role=Role.ADMIN)

        assert not self.checker.has_admin_permission(user)
        assert self.checker.has_admin_permission(admin)


class TestTaskPermissionHelper:
    """任务权限辅助函数测试"""

    @pytest.mark.asyncio
    async def test_check_task_permission(self):
        """测试任务权限检查辅助函数"""
        user = User(
            id="user7",
            username="taskuser",
            email="taskuser@example.com",
            role=Role.USER
        )

        # 测试各种任务操作权限
        assert await check_task_permission(user, "create")
        assert await check_task_permission(user, "read")
        assert await check_task_permission(user, "update")
        assert await check_task_permission(user, "delete")
        assert await check_task_permission(user, "execute")

        # 测试无效操作
        assert not await check_task_permission(user, "invalid_action")


class TestPermissionCheckerFactory:
    """权限检查器工厂测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        # 重置实例
        PermissionCheckerFactory.reset_instance()

        # 获取两个实例应该是同一个对象
        instance1 = PermissionCheckerFactory.get_instance()
        instance2 = PermissionCheckerFactory.get_instance()

        assert instance1 is instance2

    def test_reset_instance(self):
        """测试重置实例"""
        instance1 = PermissionCheckerFactory.get_instance()
        PermissionCheckerFactory.reset_instance()
        instance2 = PermissionCheckerFactory.get_instance()

        assert instance1 is not instance2
