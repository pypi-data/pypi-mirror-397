"""Worker模块测试用例 - 验证事件驱动架构的正确性"""

import asyncio
from typing import Any, Dict

import pytest
from pydantic import BaseModel, Field
from .event_system import Event, MessageTransport, TaskContext, WorkerEventBus
from .task_handlers import task_registry


class MockTransport(MessageTransport):
    """模拟传输层"""

    def __init__(self):
        self.messages = []
        self.message_callback = None
        self.worker_id = "test_worker_123"

    def set_message_callback(self, callback):
        self.message_callback = callback

    def get_worker_id(self) -> str:
        return self.worker_id

    async def send_message(self, message: Dict[str, Any]):
        self.messages.append(message)

    async def start(self):
        pass

    async def stop(self):
        pass

    async def simulate_incoming_message(self, message_type: str, data: Dict[str, Any]):
        """模拟接收到的消息"""
        if self.message_callback:
            event = Event(type=message_type, data=data, source="test")
            await self.message_callback(event)


class TestTaskInput(BaseModel):
    """测试任务输入"""

    taskId: str = Field(..., description="任务ID")
    test_data: str = Field(default="test", description="测试数据")


class TestTaskOutput(BaseModel):
    """测试任务输出"""

    result: str = Field(..., description="测试结果")
    duration: float = Field(..., description="执行时长")
    test_value: str = Field(..., description="测试值")


@task_registry.task(
    "test_task", input_validator=TestTaskInput, output_validator=TestTaskOutput
)
async def handle_test_task(
    input_data: TestTaskInput, ctx: TaskContext
) -> TestTaskOutput:
    """测试任务处理器"""
    await ctx.log(f"执行测试任务: {input_data.taskId}")

    await asyncio.sleep(0.1)

    result = (
        f"Test task {input_data.taskId} completed with data: {input_data.test_data}"
    )

    await ctx.log(f"测试任务完成: {result}")

    return TestTaskOutput(
        result=result, duration=0.1, test_value=f"processed_{input_data.test_data}"
    )


@pytest.mark.asyncio
async def test_worker_initialization():
    """测试Worker初始化"""
    mock_transport = MockTransport()
    event_bus = WorkerEventBus(mock_transport)

    assert event_bus.transport == mock_transport
    assert event_bus.worker_id == "test_worker_123"


@pytest.mark.asyncio
async def test_event_system():
    """测试事件系统"""
    mock_transport = MockTransport()
    event_bus = WorkerEventBus(mock_transport)

    received_events = []

    async def test_handler(event: Event):
        received_events.append(event)

    event_bus.on_event("test_event", test_handler)

    await mock_transport.simulate_incoming_message("test_event", {"test": "data"})

    assert len(received_events) == 1
    assert received_events[0].type == "test_event"
    assert received_events[0].data == {"test": "data"}


@pytest.mark.asyncio
async def test_task_processing():
    """测试任务处理"""
    mock_transport = MockTransport()
    event_bus = WorkerEventBus(mock_transport)

    event = Event(
        type="test_task", data={"taskId": "test_123", "test_data": "hello_world"}
    )
    ctx = TaskContext(event_bus, "test_123", event)

    handler = task_registry.get_handler("test_task")
    assert handler is not None
    result = await handler(ctx)
    assert isinstance(result, TestTaskOutput)
    assert result.result == "Test task test_123 completed with data: hello_world"
    assert result.test_value == "processed_hello_world"
    assert result.duration == 0.1


@pytest.mark.asyncio
async def test_task_context():
    """测试任务上下文功能"""
    mock_transport = MockTransport()
    event_bus = WorkerEventBus(mock_transport)

    event = Event(type="test", data={"taskId": "ctx_test"})
    ctx = TaskContext(event_bus, "ctx_test", event)
    await ctx.log("测试日志消息", "info")
    assert len(mock_transport.messages) == 1
    log_message = mock_transport.messages[0]
    assert log_message["type"] == "log"
    assert log_message["data"]["message"] == "测试日志消息"
    assert log_message["data"]["level"] == "info"
    assert log_message["data"]["taskId"] == "ctx_test"
    await ctx.send_status("running", {"progress": 50})
    assert len(mock_transport.messages) == 2
    status_message = mock_transport.messages[1]
    assert status_message["type"] == "task_status_update"
    assert status_message["data"]["status"] == "running"
    assert status_message["data"]["progress"] == 50


@pytest.mark.asyncio
async def test_message_sender():
    """测试统一的消息发送器"""
    mock_transport = MockTransport()
    event_bus = WorkerEventBus(mock_transport)
    await event_bus.message_sender.send_worker_heartbeat("busy", "task_123")

    assert len(mock_transport.messages) == 1
    heartbeat_msg = mock_transport.messages[0]
    assert heartbeat_msg["type"] == "worker_heartbeat"
    assert heartbeat_msg["data"]["status"] == "busy"
    assert heartbeat_msg["data"]["currentTask"] == "task_123"
    await event_bus.message_sender.send_task_status(
        "task_123", "completed", "Success", 2.5
    )

    assert len(mock_transport.messages) == 2
    task_msg = mock_transport.messages[1]
    assert task_msg["type"] == "task_completed"
    assert task_msg["data"]["result"] == "Success"
    assert task_msg["data"]["duration"] == 2.5

    # 测试toast消息
    await event_bus.message_sender.send_toast("测试消息")

    assert len(mock_transport.messages) == 3
    toast_msg = mock_transport.messages[2]
    assert toast_msg["type"] == "toast"
    assert toast_msg["data"]["message"] == "测试消息"

    # 测试NapCat状态消息
    await event_bus.message_sender.send_napcat_status("instance_1", "running")

    assert len(mock_transport.messages) == 4
    napcat_msg = mock_transport.messages[3]
    assert napcat_msg["type"] == "napcat_status_update"
    assert napcat_msg["data"]["instanceId"] == "instance_1"
    assert napcat_msg["data"]["status"] == "running"


@pytest.mark.asyncio
async def test_ping_task():
    """测试ping任务"""
    mock_transport = MockTransport()
    event_bus = WorkerEventBus(mock_transport)

    # 创建ping任务上下文
    event = Event(type="ping_test", data={"taskId": "ping_123", "message": "hello"})
    ctx = TaskContext(event_bus, "ping_123", event)

    # 获取并执行ping任务处理器
    handler = task_registry.get_handler("ping_test")
    assert handler is not None

    # 执行任务
    result = await handler(ctx)

    # 验证结果
    assert result.result == "Ping test completed for task ping_123"
    assert result.echo_message == "Echo: hello"
    assert result.duration == 1.0


def test_task_registry():
    """测试任务注册表"""
    # 验证任务已注册
    registered_tasks = task_registry.list_tasks()
    assert "test_task" in registered_tasks
    assert "ping_test" in registered_tasks
    assert "start_napcat" in registered_tasks

    # 验证可以获取处理器
    test_handler = task_registry.get_handler("test_task")
    assert test_handler is not None

    ping_handler = task_registry.get_handler("ping_test")
    assert ping_handler is not None


if __name__ == "__main__":

    async def run_simple_test():
        print("运行Worker模块简单测试...")
        mock_transport = MockTransport()
        event_bus = WorkerEventBus(mock_transport)

        print("✓ 事件总线创建成功")

        tasks = task_registry.list_tasks()
        print(f"✓ 已注册任务: {tasks}")

        event = Event(
            type="ping_test", data={"taskId": "simple_test", "message": "test"}
        )
        ctx = TaskContext(event_bus, "simple_test", event)

        handler = task_registry.get_handler("ping_test")
        if handler:
            result = await handler(ctx)
            print(f"✓ 任务执行成功: {result.result}")

        print("✓ 所有测试通过！")

    asyncio.run(run_simple_test())
