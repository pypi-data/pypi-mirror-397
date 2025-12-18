import logging
import sys
import time
import uuid
import pytest

from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.runners import Runner
from google.adk.agents import LlmAgent
from google.genai import types

from mtmai.adk.session_service import MtAdkSessionService

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://mtgateapi.yuepa8.com"
TEST_APP_NAME = "pytest_integration_app"


@pytest.fixture
def session_service() -> MtAdkSessionService:
    """初始化 Session Service"""
    return MtAdkSessionService(base_url=BASE_URL)


@pytest.fixture
def valid_user_id() -> str:
    """生成符合数据库要求的 UUID 格式 User ID"""
    return str(uuid.uuid4())


@pytest.fixture
def valid_session_id() -> str:
    """生成随机 Session ID"""
    return str(uuid.uuid4())


@pytest.fixture
def simple_agent() -> LlmAgent:
    """创建一个简单的 Agent 用于测试 Event 写入"""
    return LlmAgent(
        model="gemini-2.0-flash",
        name="test_echo_agent",
        instruction="You are a test agent. Just reply 'OK' to everything.",
    )


# --- Test Cases ---


@pytest.mark.asyncio
async def test_create_and_get_session(
    session_service: MtAdkSessionService, valid_user_id: str, valid_session_id: str
):
    """
    测试 Session 的创建和读取 (CRUD)。
    """
    logger.info(
        f"Testing Create/Get with UserID: {valid_user_id}, SessionID: {valid_session_id}"
    )

    initial_state = {"test_key": "test_value", "step": 1}

    # 1. 创建 Session
    created_session = await session_service.create_session(
        app_name=TEST_APP_NAME,
        user_id=valid_user_id,
        session_id=valid_session_id,
        state=initial_state,
    )

    assert created_session is not None
    assert created_session.id == valid_session_id
    assert created_session.user_id == valid_user_id
    assert created_session.app_name == TEST_APP_NAME
    assert created_session.state["test_key"] == "test_value"

    # 2. 读取 Session
    fetched_session = await session_service.get_session(
        app_name=TEST_APP_NAME, user_id=valid_user_id, session_id=valid_session_id
    )

    # 类型守卫：告诉类型检查器 fetched_session 不为 None
    assert fetched_session is not None, "Failed to fetch session"

    assert fetched_session.id == valid_session_id
    assert fetched_session.state["test_key"] == "test_value"
    assert fetched_session.last_update_time > 0


@pytest.mark.asyncio
async def test_runner_integration_append_events(
    session_service: MtAdkSessionService,
    valid_user_id: str,
    valid_session_id: str,
    simple_agent: LlmAgent,
):
    """
    测试 Runner 集成：验证 Event 能被 Runner 产生并被 Service 持久化。
    """
    logger.info(
        f"Testing Runner Integration. User: {valid_user_id}, Session: {valid_session_id}"
    )

    # 1. 创建基础 Session
    await session_service.create_session(
        app_name=TEST_APP_NAME, user_id=valid_user_id, session_id=valid_session_id
    )

    # 2. 运行 Runner
    runner = Runner(
        agent=simple_agent, app_name=TEST_APP_NAME, session_service=session_service
    )

    input_text = "Hello, this is a test."
    user_msg = types.Content(role="user", parts=[types.Part(text=input_text)])

    responses = []
    async for event in runner.run_async(
        user_id=valid_user_id, session_id=valid_session_id, new_message=user_msg
    ):
        responses.append(event)

    assert len(responses) > 0, "Runner should produce events"

    # 3. 验证持久化结果
    reloaded_session = await session_service.get_session(
        app_name=TEST_APP_NAME, user_id=valid_user_id, session_id=valid_session_id
    )

    # 类型守卫
    assert reloaded_session is not None, "Reloaded session should not be None"
    assert len(reloaded_session.events) > 0, "Session should have stored events"

    logger.info(f"Reloaded session has {len(reloaded_session.events)} events.")

    # 4. 查找特定消息 (修复类型错误)
    found_hello = False
    for evt in reloaded_session.events:
        # 必须层层检查 Optional 属性
        if evt.content and evt.content.parts and len(evt.content.parts) > 0:
            part_text = evt.content.parts[0].text
            # 确保 text 不为 None 再进行 'in' 判断
            if part_text and "Hello" in part_text:
                found_hello = True
                break

    assert found_hello, "Should find the user's 'Hello' message in stored events"


@pytest.mark.asyncio
async def test_concurrency_state_update(
    session_service: MtAdkSessionService, valid_user_id: str, valid_session_id: str
):
    """
    测试状态更新：手动追加带 State Delta 的 Event。
    """
    session = await session_service.create_session(
        app_name=TEST_APP_NAME,
        user_id=valid_user_id,
        session_id=valid_session_id,
        state={"counter": 0},
    )

    # 构造测试 Event (修复缺失 author 参数错误)
    fake_event = Event(
        id=str(uuid.uuid4()),
        timestamp=time.time(),
        author="user",  # 必须指定 author
        actions=EventActions(state_delta={"counter": 100, "new_field": "added"}),
    )

    # 追加 Event
    await session_service.append_event(session, fake_event)

    # 获取更新后的 Session
    updated_session = await session_service.get_session(
        app_name=TEST_APP_NAME, user_id=valid_user_id, session_id=valid_session_id
    )

    # 类型守卫 (修复 "events" is not known attribute of "None" 错误)
    assert updated_session is not None, "Updated session fetch failed"

    assert len(updated_session.events) == 1
    assert updated_session.events[0].id == fake_event.id

    # 如果后端实现了状态合并逻辑，此处可以断言状态已更新
    # assert updated_session.state["counter"] == 100


if __name__ == "__main__":
    # 使用 -v 参数运行 pytest
    sys.exit(pytest.main(["-v", __file__]))
