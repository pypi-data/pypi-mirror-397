"""任务定义模块 - 使用修饰器模式定义各种任务处理器"""

import asyncio
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field

from .event_system import TaskContext
from .task_handlers import TaskOutput, task_registry

logger = logging.getLogger(__name__)


class PingTestInput(BaseModel):
    """Ping测试任务输入"""

    taskId: str = Field(..., description="任务ID")
    message: str = Field(default="ping", description="测试消息")


class PingTestOutput(BaseModel):
    """Ping测试任务输出"""

    result: str = Field(..., description="测试结果")
    duration: float = Field(..., description="执行时长")
    echo_message: str = Field(..., description="回显消息")


class StartNapcatInput(BaseModel):
    """启动NapCat任务输入"""

    taskId: str = Field(..., description="任务ID")
    instance_id: str = Field(default="", description="实例ID")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置参数")


class StartNapcatOutput(BaseModel):
    """启动NapCat任务输出"""

    result: str = Field(..., description="启动结果")
    duration: float = Field(..., description="执行时长")
    instance_id: str = Field(..., description="实例ID")
    status: str = Field(..., description="状态")


class StartChatbotInput(BaseModel):
    """启动聊天机器人任务输入"""

    taskId: str = Field(..., description="任务ID")
    chatbot_id: str = Field(..., description="聊天机器人ID")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置参数")


class StartChatbotOutput(BaseModel):
    """启动聊天机器人任务输出"""

    result: str = Field(..., description="启动结果")
    duration: float = Field(..., description="执行时长")
    chatbot_id: str = Field(..., description="聊天机器人ID")
    status: str = Field(..., description="状态")


class StopChatbotInput(BaseModel):
    """停止聊天机器人任务输入"""

    taskId: str = Field(..., description="任务ID")
    chatbot_id: str = Field(..., description="聊天机器人ID")


class StopChatbotOutput(BaseModel):
    """停止聊天机器人任务输出"""

    result: str = Field(..., description="停止结果")
    duration: float = Field(..., description="执行时长")
    chatbot_id: str = Field(..., description="聊天机器人ID")
    status: str = Field(..., description="状态")


@task_registry.task(
    "ping_test", input_validator=PingTestInput, output_validator=PingTestOutput
)
async def handle_ping_test(
    input_data: PingTestInput, ctx: TaskContext
) -> PingTestOutput:
    """处理ping测试任务"""
    await ctx.log(f"开始执行ping测试任务: {input_data.taskId}")
    await asyncio.sleep(1)

    result = f"Ping test completed for task {input_data.taskId}"
    echo_message = f"Echo: {input_data.message}"

    await ctx.log(f"Ping测试完成: {result}")

    return PingTestOutput(result=result, duration=1.0, echo_message=echo_message)


@task_registry.task(
    "start_napcat", input_validator=StartNapcatInput, output_validator=StartNapcatOutput
)
async def handle_start_napcat(
    input_data: StartNapcatInput, ctx: TaskContext
) -> StartNapcatOutput:
    """处理启动NapCat任务"""
    await ctx.log(f"开始启动NapCat容器: {input_data.taskId}")

    try:
        # 导入napcat处理器
        from .napcat_handler import NapcatHandler

        napcat_handler = NapcatHandler()

        # 调用napcat处理器
        result, duration = await napcat_handler.handle_start_napcat_task(
            ctx.event_bus, input_data.taskId, input_data.model_dump()
        )

        # 确定实例ID
        instance_id = input_data.instance_id or f"worker_{ctx.event_bus.worker_id}"

        await ctx.log(f"NapCat启动完成: {result}")

        return StartNapcatOutput(
            result=result, duration=duration, instance_id=instance_id, status="success"
        )

    except Exception as e:
        error_msg = f"启动NapCat失败: {str(e)}"
        await ctx.log(error_msg, "error")

        return StartNapcatOutput(
            result=error_msg,
            duration=0.0,
            instance_id=input_data.instance_id or f"worker_{ctx.event_bus.worker_id}",
            status="error",
        )


@task_registry.task(
    "start_chatbot",
    input_validator=StartChatbotInput,
    output_validator=StartChatbotOutput,
)
async def handle_start_chatbot(
    input_data: StartChatbotInput, ctx: TaskContext
) -> StartChatbotOutput:
    """处理启动聊天机器人任务"""
    await ctx.log(f"开始启动聊天机器人: {input_data.chatbot_id}")

    try:
        # 导入聊天机器人处理器
        from .chatbot_handler import ChatbotHandler

        chatbot_handler = ChatbotHandler()

        # 调用聊天机器人处理器
        result, duration = await chatbot_handler.handle_start_chatbot_task(
            ctx.event_bus, input_data.taskId, input_data.model_dump()
        )

        await ctx.log(f"聊天机器人启动完成: {result}")

        return StartChatbotOutput(
            result=result,
            duration=duration,
            chatbot_id=input_data.chatbot_id,
            status="success",
        )

    except Exception as e:
        error_msg = f"启动聊天机器人失败: {str(e)}"
        await ctx.log(error_msg, "error")

        return StartChatbotOutput(
            result=error_msg,
            duration=0.0,
            chatbot_id=input_data.chatbot_id,
            status="error",
        )


@task_registry.task(
    "stop_chatbot", input_validator=StopChatbotInput, output_validator=StopChatbotOutput
)
async def handle_stop_chatbot(
    input_data: StopChatbotInput, ctx: TaskContext
) -> StopChatbotOutput:
    """处理停止聊天机器人任务"""
    await ctx.log(f"开始停止聊天机器人: {input_data.chatbot_id}")

    try:
        # 导入聊天机器人处理器
        from .chatbot_handler import ChatbotHandler

        chatbot_handler = ChatbotHandler()

        # 调用聊天机器人处理器
        result, duration = await chatbot_handler.handle_stop_chatbot_task(
            ctx.event_bus, input_data.taskId, input_data.model_dump()
        )

        await ctx.log(f"聊天机器人停止完成: {result}")

        return StopChatbotOutput(
            result=result,
            duration=duration,
            chatbot_id=input_data.chatbot_id,
            status="success",
        )

    except Exception as e:
        error_msg = f"停止聊天机器人失败: {str(e)}"
        await ctx.log(error_msg, "error")

        return StopChatbotOutput(
            result=error_msg,
            duration=0.0,
            chatbot_id=input_data.chatbot_id,
            status="error",
        )


@task_registry.task("default_task")
async def handle_default_task(ctx: TaskContext) -> TaskOutput:
    """处理默认任务"""
    task_id = ctx.task_id
    task_type = ctx.event.type

    await ctx.log(f"执行默认任务: {task_type}")

    # 模拟任务执行
    await asyncio.sleep(2)

    result = f"Task {task_id} of type {task_type} completed successfully"

    await ctx.log(f"默认任务完成: {result}")

    return TaskOutput(result=result, duration=2.0, success=True)


# 导出任务注册表，供其他模块使用
__all__ = [
    "task_registry",
    "handle_ping_test",
    "handle_start_napcat",
    "handle_start_chatbot",
    "handle_stop_chatbot",
    "handle_default_task",
]
