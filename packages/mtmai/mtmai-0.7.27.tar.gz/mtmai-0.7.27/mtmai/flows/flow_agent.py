import logging

from hatchet_sdk import Context
from pydantic import BaseModel

from mtmai.hatchet_client import hatchet
from mtmai.mtlibs.gomtm_api_client import GomtmApiClient, http_url_to_ws_url
from mtmai.mtlibs.napcat_client import get_sandbox_manager

logger = logging.getLogger(__name__)


class FlowAgentInput(BaseModel):
    id: str
    mtmapi_url: str = "https://ht-gomtm.yuepa8.com"
    mtmapi_api_token: str = ""


class FlowAgentOutput(BaseModel):
    success: bool
    message: str


class AgentStep1Output(BaseModel):
    is_wait_for_login: bool = False


flow_agent = hatchet.workflow(
    name="agent-start-workflow",
    input_validator=FlowAgentInput,
    on_events=["agent_updated"],
)


@flow_agent.task()
async def step_agent_instance_init(
    input: FlowAgentInput, ctx: Context
) -> AgentStep1Output:
    """智能体实例初始化步骤"""
    ctx.log("step-agent-instance-init 开始")

    # 发送测试事件 (暂时注释掉，因为Python SDK可能有不同的实现方式)
    # test_event = {"test": "test"}
    # ctx.stream_event(test_event)

    if not input.id:
        raise ValueError("AgentId为空，无法启动napcat服务")

    # 创建API客户端
    async with GomtmApiClient(input.mtmapi_url, input.mtmapi_api_token) as api_client:
        # 获取智能体信息
        agent = await api_client.get_agent(input.id)

        if agent.get("name") != "chatbot":
            raise ValueError("目前仅支持 chatbot 类型的agent启动napcat服务")

        # 获取沙盒管理器
        sandbox_manager = get_sandbox_manager()

        # 创建napcat沙盒
        instance_id = input.id[:8]
        napcat_client = await sandbox_manager.get_or_create_napcat_sandbox(instance_id)

        try:
            # 获取登录二维码
            qr_code_url = await napcat_client.get_qq_login_qrcode()
            ctx.log(f"获取到登录二维码: {qr_code_url}")

            # 更新智能体状态
            state = agent.get("state", {})
            state["napcat_webui_api_url"] = napcat_client.url
            state["qrcode_url"] = qr_code_url

            await api_client.update_agent_state(input.id, state, "active")
            ctx.log(f"已更新智能体状态: {state}")

            # 等待QQ登录
            try:
                self_id = await napcat_client.wait_qq_login(timeout=120)
                state["selfId"] = self_id
                await api_client.update_agent_state(input.id, state, "active")
                ctx.log(f"QQ登录成功，selfId: {self_id}")
            except TimeoutError:
                ctx.log("QQ 未登录,等待扫描超时")

        except Exception as e:
            ctx.log(f"创建napcat沙盒失败: {e}")
            # 清理无效客户端
            sandbox_manager.remove_invalid_client(instance_id)
            raise

    return AgentStep1Output(is_wait_for_login=False)


@flow_agent.task(parents=[step_agent_instance_init])
async def step_onebot_init(input: FlowAgentInput, ctx: Context) -> FlowAgentOutput:
    """OneBot初始化步骤"""
    ctx.log("step-onebot-init 开始")

    # 获取上一步的输出 (暂时不使用)
    # step1_output = ctx.parent_output(step_agent_instance_init)

    async with GomtmApiClient(input.mtmapi_url, input.mtmapi_api_token) as api_client:
        # 获取智能体信息
        agent = await api_client.get_agent(input.id)

        state = agent.get("state", {})
        napcat_webui_api_url = state.get("napcat_webui_api_url")

        if not napcat_webui_api_url:
            return FlowAgentOutput(success=False, message="未找到napcat API URL")

        # 获取napcat客户端
        sandbox_manager = get_sandbox_manager()
        instance_id = input.id[:8]
        napcat_client = await sandbox_manager.get_or_create_napcat_sandbox(instance_id)

        # 设置OneBot11反向WebSocket
        gomtm_onebot_ws_endpoint = (
            f"{http_url_to_ws_url(input.mtmapi_url)}/api/v2/onebot11/ws"
        )
        ctx.log(f"gomtmOnebotWsEndpoint: {gomtm_onebot_ws_endpoint}")

        try:
            await napcat_client.setup_onebot11_reverse_websocket(
                gomtm_onebot_ws_endpoint
            )

            # 更新智能体状态
            state["is_napcat_ready"] = True
            state["onebot_ws_endpoint"] = gomtm_onebot_ws_endpoint

            await api_client.update_agent_state(input.id, state)

            return FlowAgentOutput(success=True, message="OneBot11设置成功")

        except Exception as e:
            ctx.log(f"设置OneBot11反向WebSocket失败: {e}")
            return FlowAgentOutput(success=False, message=f"设置OneBot11失败: {e}")
