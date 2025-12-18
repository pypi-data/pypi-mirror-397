"""
任务执行器测试用例
测试AsyncExecutor和AsyncExecutorFactory的功能
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import BackgroundTasks, Request

from mtmai.executor.factory import AsyncExecutor, AsyncExecutorFactory


class TestAsyncExecutor:
    """异步执行器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.executor = AsyncExecutor()
        self.mock_request = Mock(spec=Request)
        self.mock_request.method = "POST"
        self.mock_request.url = "http://test.com/api/tasks"
        self.mock_request.headers = {"Authorization": "Bearer test-token"}
        self.background_tasks = BackgroundTasks()

    @pytest.mark.asyncio
    async def test_execute_graph_basic(self):
        """测试基本的图执行功能"""
        result = await self.executor.execute_graph(
            request=self.mock_request,
            background_tasks=self.background_tasks,
            graph_id="taskrunner",
            thread_id="test-thread-123"
        )

        # 验证返回结果
        assert "execution_id" in result
        assert result["status"] == "submitted"
        assert result["graph_id"] == "taskrunner"
        assert result["thread_id"] == "test-thread-123"
        assert result["message"] == "Task submitted for background execution"

    @pytest.mark.asyncio
    async def test_execute_graph_with_optional_params(self):
        """测试带可选参数的图执行"""
        result = await self.executor.execute_graph(
            request=self.mock_request,
            background_tasks=self.background_tasks,
            graph_id="storm",
            thread_id="test-thread-456",
            task_type="research",
            organization_id="org-123",
            max_steps_override=50,
            api_key="test-api-key",
            user_id="user-789"
        )

        assert result["graph_id"] == "storm"
        assert result["thread_id"] == "test-thread-456"
        assert result["status"] == "submitted"

    @pytest.mark.asyncio
    async def test_execute_graph_missing_required_params(self):
        """测试缺少必需参数的情况"""
        # 缺少graph_id
        with pytest.raises(ValueError, match="graph_id is required"):
            await self.executor.execute_graph(
                request=self.mock_request,
                background_tasks=self.background_tasks,
                graph_id="",
                thread_id="test-thread"
            )

        # 缺少thread_id
        with pytest.raises(ValueError, match="thread_id is required"):
            await self.executor.execute_graph(
                request=self.mock_request,
                background_tasks=self.background_tasks,
                graph_id="taskrunner",
                thread_id=""
            )

    @pytest.mark.asyncio
    async def test_execute_taskrunner_graph(self):
        """测试taskrunner图执行"""
        task_config = {
            "execution_id": "test-exec-1",
            "graph_id": "taskrunner",
            "thread_id": "test-thread",
            "task_type": "analysis"
        }

        result = await self.executor._execute_taskrunner_graph(task_config)

        assert result["type"] == "taskrunner"
        assert result["status"] == "completed"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_storm_graph(self):
        """测试storm图执行"""
        task_config = {
            "execution_id": "test-exec-2",
            "graph_id": "storm",
            "thread_id": "test-thread",
            "task_type": "research"
        }

        result = await self.executor._execute_storm_graph(task_config)

        assert result["type"] == "storm"
        assert result["status"] == "completed"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_canvas_graph(self):
        """测试canvas图执行"""
        task_config = {
            "execution_id": "test-exec-3",
            "graph_id": "canvas",
            "thread_id": "test-thread",
            "task_type": "writing"
        }

        result = await self.executor._execute_canvas_graph(task_config)

        assert result["type"] == "canvas"
        assert result["status"] == "completed"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_default_graph(self):
        """测试默认图执行"""
        task_config = {
            "execution_id": "test-exec-4",
            "graph_id": "unknown",
            "thread_id": "test-thread",
            "task_type": "default"
        }

        result = await self.executor._execute_default_graph(task_config)

        assert result["type"] == "default"
        assert result["status"] == "completed"
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_graph_background_taskrunner(self):
        """测试后台执行taskrunner图"""
        task_config = {
            "execution_id": "test-exec-5",
            "graph_id": "taskrunner",
            "thread_id": "test-thread",
            "task_type": "analysis"
        }

        # 这个方法不返回值，但不应该抛出异常
        await self.executor._execute_graph_background(task_config)

    @pytest.mark.asyncio
    async def test_execute_graph_background_storm(self):
        """测试后台执行storm图"""
        task_config = {
            "execution_id": "test-exec-6",
            "graph_id": "storm",
            "thread_id": "test-thread",
            "task_type": "research"
        }

        await self.executor._execute_graph_background(task_config)

    @pytest.mark.asyncio
    async def test_execute_graph_background_canvas(self):
        """测试后台执行canvas图"""
        task_config = {
            "execution_id": "test-exec-7",
            "graph_id": "canvas",
            "thread_id": "test-thread",
            "task_type": "writing"
        }

        await self.executor._execute_graph_background(task_config)

    @pytest.mark.asyncio
    async def test_execute_graph_background_unknown(self):
        """测试后台执行未知图类型"""
        task_config = {
            "execution_id": "test-exec-8",
            "graph_id": "unknown_graph",
            "thread_id": "test-thread",
            "task_type": "unknown"
        }

        # 应该使用默认执行器
        await self.executor._execute_graph_background(task_config)

    @pytest.mark.asyncio
    async def test_get_task_status(self):
        """测试获取任务状态"""
        # 不存在的任务
        status = await self.executor.get_task_status("non-existent")
        assert status is None

        # 模拟运行中的任务
        mock_task = AsyncMock()
        mock_task.done.return_value = False
        self.executor.running_tasks["test-exec-9"] = mock_task

        status = await self.executor.get_task_status("test-exec-9")
        assert status is not None
        assert status["execution_id"] == "test-exec-9"
        assert status["status"] == "running"
        assert status["done"] is False

    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """测试取消任务"""
        # 不存在的任务
        result = await self.executor.cancel_task("non-existent")
        assert result is False

        # 模拟运行中的任务
        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = Mock()
        self.executor.running_tasks["test-exec-10"] = mock_task

        result = await self.executor.cancel_task("test-exec-10")
        assert result is True
        mock_task.cancel.assert_called_once()


class TestAsyncExecutorFactory:
    """异步执行器工厂测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 重置工厂实例
        AsyncExecutorFactory.reset_executor()

    def test_singleton_pattern(self):
        """测试单例模式"""
        executor1 = AsyncExecutorFactory.get_executor()
        executor2 = AsyncExecutorFactory.get_executor()

        assert executor1 is executor2
        assert isinstance(executor1, AsyncExecutor)

    def test_reset_executor(self):
        """测试重置执行器"""
        executor1 = AsyncExecutorFactory.get_executor()
        AsyncExecutorFactory.reset_executor()
        executor2 = AsyncExecutorFactory.get_executor()

        assert executor1 is not executor2
        assert isinstance(executor2, AsyncExecutor)


class TestTaskConfigGeneration:
    """任务配置生成测试"""

    def setup_method(self):
        self.executor = AsyncExecutor()
        self.mock_request = Mock(spec=Request)
        self.mock_request.method = "POST"
        self.mock_request.url = "http://test.com/api/tasks"
        self.mock_request.headers = {"Authorization": "Bearer test-token"}
        self.background_tasks = BackgroundTasks()

    @pytest.mark.asyncio
    async def test_task_config_structure(self):
        """测试任务配置结构"""
        # 通过执行图任务来验证配置结构
        result = await self.executor.execute_graph(
            request=self.mock_request,
            background_tasks=self.background_tasks,
            graph_id="taskrunner",
            thread_id="test-thread",
            task_type="analysis",
            organization_id="org-123",
            max_steps_override=30,
            api_key="test-key",
            user_id="user-456"
        )

        # 验证基本返回结构
        assert "execution_id" in result
        assert result["graph_id"] == "taskrunner"
        assert result["thread_id"] == "test-thread"
