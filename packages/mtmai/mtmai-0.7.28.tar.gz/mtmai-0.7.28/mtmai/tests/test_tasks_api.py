"""
任务API集成测试
测试任务创建、列表查询的权限检测和执行优化功能
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from mtmai.api.tasks import _determine_graph_id, _get_max_steps_for_task_type
from mtmai.auth.permissions import User, Role, Permission


class TestTaskAPIHelpers:
    """任务API辅助函数测试"""

    def test_determine_graph_id(self):
        """测试图ID确定逻辑"""
        # 测试已知任务类型
        assert _determine_graph_id("storm") == "storm"
        assert _determine_graph_id("canvas") == "canvas"
        assert _determine_graph_id("research") == "storm"
        assert _determine_graph_id("writing") == "canvas"
        assert _determine_graph_id("analysis") == "taskrunner"

        # 测试未知任务类型
        assert _determine_graph_id("unknown_type") == "taskrunner"
        assert _determine_graph_id("") == "taskrunner"
        assert _determine_graph_id(None) == "taskrunner"

    def test_get_max_steps_for_task_type(self):
        """测试最大步骤数确定逻辑"""
        # 测试已知任务类型
        assert _get_max_steps_for_task_type("storm") == 50
        assert _get_max_steps_for_task_type("canvas") == 30
        assert _get_max_steps_for_task_type("research") == 50
        assert _get_max_steps_for_task_type("writing") == 30
        assert _get_max_steps_for_task_type("analysis") == 20

        # 测试未知任务类型
        assert _get_max_steps_for_task_type("unknown_type") == 25
        assert _get_max_steps_for_task_type("") == 25
        assert _get_max_steps_for_task_type(None) == 25


class TestTaskPermissionIntegration:
    """任务权限集成测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建测试用户
        self.normal_user = User(
            id="user1",
            username="normaluser",
            email="normal@example.com",
            role=Role.USER,
            organization_id="org1"
        )

        self.admin_user = User(
            id="admin1",
            username="adminuser",
            email="admin@example.com",
            role=Role.ADMIN,
            organization_id="org1"
        )

        self.inactive_user = User(
            id="inactive1",
            username="inactiveuser",
            email="inactive@example.com",
            role=Role.USER,
            is_active=False
        )

        self.guest_user = User(
            id="guest1",
            username="guestuser",
            email="guest@example.com",
            role=Role.GUEST
        )

    @pytest.mark.asyncio
    async def test_task_list_permission_normal_user(self):
        """测试普通用户的任务列表权限"""
        from mtmai.auth.permissions import check_task_permission

        # 普通用户应该能够读取任务
        has_permission = await check_task_permission(self.normal_user, "read")
        assert has_permission is True

    @pytest.mark.asyncio
    async def test_task_list_permission_guest_user(self):
        """测试访客用户的任务列表权限"""
        from mtmai.auth.permissions import check_task_permission

        # 访客用户应该能够读取任务
        has_permission = await check_task_permission(self.guest_user, "read")
        assert has_permission is True

    @pytest.mark.asyncio
    async def test_task_list_permission_inactive_user(self):
        """测试未激活用户的任务列表权限"""
        from mtmai.auth.permissions import check_task_permission

        # 未激活用户不应该有任何权限
        has_permission = await check_task_permission(self.inactive_user, "read")
        assert has_permission is False

    @pytest.mark.asyncio
    async def test_task_create_permission_normal_user(self):
        """测试普通用户的任务创建权限"""
        from mtmai.auth.permissions import check_task_permission

        # 普通用户应该能够创建和执行任务
        has_create_permission = await check_task_permission(self.normal_user, "create")
        has_execute_permission = await check_task_permission(self.normal_user, "execute")

        assert has_create_permission is True
        assert has_execute_permission is True

    @pytest.mark.asyncio
    async def test_task_create_permission_guest_user(self):
        """测试访客用户的任务创建权限"""
        from mtmai.auth.permissions import check_task_permission

        # 访客用户不应该能够创建任务
        has_create_permission = await check_task_permission(self.guest_user, "create")
        has_execute_permission = await check_task_permission(self.guest_user, "execute")

        assert has_create_permission is False
        assert has_execute_permission is False

    @pytest.mark.asyncio
    async def test_task_create_permission_admin_user(self):
        """测试管理员用户的任务创建权限"""
        from mtmai.auth.permissions import check_task_permission

        # 管理员应该具有所有任务权限
        has_create_permission = await check_task_permission(self.admin_user, "create")
        has_execute_permission = await check_task_permission(self.admin_user, "execute")
        has_read_permission = await check_task_permission(self.admin_user, "read")
        has_update_permission = await check_task_permission(self.admin_user, "update")
        has_delete_permission = await check_task_permission(self.admin_user, "delete")

        assert has_create_permission is True
        assert has_execute_permission is True
        assert has_read_permission is True
        assert has_update_permission is True
        assert has_delete_permission is True


class TestTaskExecutionOptimization:
    """任务执行优化测试"""

    def test_graph_id_optimization(self):
        """测试图ID优化逻辑"""
        # 验证不同任务类型映射到正确的图ID
        test_cases = [
            ("storm", "storm"),
            ("research", "storm"),  # 研究类任务使用storm图
            ("canvas", "canvas"),
            ("writing", "canvas"),  # 写作类任务使用canvas图
            ("analysis", "taskrunner"),  # 分析类任务使用taskrunner图
            ("unknown", "taskrunner"),  # 未知类型使用默认taskrunner图
        ]

        for task_type, expected_graph_id in test_cases:
            actual_graph_id = _determine_graph_id(task_type)
            assert actual_graph_id == expected_graph_id, f"任务类型 {task_type} 应该映射到 {expected_graph_id}，但实际是 {actual_graph_id}"

    def test_max_steps_optimization(self):
        """测试最大步骤数优化逻辑"""
        # 验证不同任务类型的最大步骤数配置
        test_cases = [
            ("storm", 50),      # 研究类任务需要更多步骤
            ("research", 50),   # 研究类任务
            ("canvas", 30),     # 创作类任务中等步骤
            ("writing", 30),    # 写作类任务
            ("analysis", 20),   # 分析类任务较少步骤
            ("unknown", 25),    # 未知类型使用默认步骤数
        ]

        for task_type, expected_max_steps in test_cases:
            actual_max_steps = _get_max_steps_for_task_type(task_type)
            assert actual_max_steps == expected_max_steps, f"任务类型 {task_type} 应该有 {expected_max_steps} 步骤，但实际是 {actual_max_steps}"

    def test_task_type_to_resource_mapping(self):
        """测试任务类型到资源的映射逻辑"""
        # 验证资源密集型任务分配更多步骤
        resource_intensive_tasks = ["storm", "research"]
        moderate_tasks = ["canvas", "writing"]
        light_tasks = ["analysis"]

        for task_type in resource_intensive_tasks:
            max_steps = _get_max_steps_for_task_type(task_type)
            assert max_steps >= 50, f"资源密集型任务 {task_type} 应该有至少50步骤"

        for task_type in moderate_tasks:
            max_steps = _get_max_steps_for_task_type(task_type)
            assert 25 <= max_steps <= 35, f"中等任务 {task_type} 应该有25-35步骤"

        for task_type in light_tasks:
            max_steps = _get_max_steps_for_task_type(task_type)
            assert max_steps <= 25, f"轻量任务 {task_type} 应该有不超过25步骤"


class TestTaskAPIErrorHandling:
    """任务API错误处理测试"""

    @pytest.mark.asyncio
    async def test_permission_denied_scenarios(self):
        """测试权限拒绝场景"""
        from mtmai.auth.permissions import check_task_permission

        # 创建无权限用户
        no_permission_user = User(
            id="noperm1",
            username="nopermuser",
            email="noperm@example.com",
            role=Role.GUEST,  # 访客角色对某些操作无权限
            is_active=True
        )

        # 测试创建权限被拒绝
        has_create_permission = await check_task_permission(no_permission_user, "create")
        assert has_create_permission is False

        # 测试执行权限被拒绝
        has_execute_permission = await check_task_permission(no_permission_user, "execute")
        assert has_execute_permission is False

    @pytest.mark.asyncio
    async def test_invalid_task_action(self):
        """测试无效任务操作"""
        from mtmai.auth.permissions import check_task_permission

        user = User(
            id="user1",
            username="testuser",
            email="test@example.com",
            role=Role.USER
        )

        # 测试无效操作返回False
        has_permission = await check_task_permission(user, "invalid_action")
        assert has_permission is False

    def test_edge_cases_in_helpers(self):
        """测试辅助函数的边界情况"""
        # 测试None值
        assert _determine_graph_id(None) == "taskrunner"
        assert _get_max_steps_for_task_type(None) == 25

        # 测试空字符串
        assert _determine_graph_id("") == "taskrunner"
        assert _get_max_steps_for_task_type("") == 25

        # 测试特殊字符
        assert _determine_graph_id("@#$%") == "taskrunner"
        assert _get_max_steps_for_task_type("@#$%") == 25
