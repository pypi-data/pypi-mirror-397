"""测试Python版本的智能体工作流"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mtmai.flows.flow_agent import AgentStep1Output, FlowAgentInput, FlowAgentOutput


class TestFlowAgent:
    """测试智能体工作流"""

    def test_flow_agent_input_validation(self):
        """测试输入数据验证"""
        # 测试有效输入
        valid_input = FlowAgentInput(
            id="test-agent-123",
            mtmapi_url="https://api.example.com",
            mtmapi_api_token="test-token",
        )
        assert valid_input.id == "test-agent-123"
        assert valid_input.mtmapi_url == "https://api.example.com"
        assert valid_input.mtmapi_api_token == "test-token"

        # 测试默认值
        minimal_input = FlowAgentInput(id="test-agent-456")
        assert minimal_input.mtmapi_url == "https://ht-gomtm.yuepa8.com"
        assert minimal_input.mtmapi_api_token == ""

    def test_flow_agent_output_validation(self):
        """测试输出数据验证"""
        output = FlowAgentOutput(success=True, message="测试成功")
        assert output.success is True
        assert output.message == "测试成功"

    def test_agent_step1_output_validation(self):
        """测试步骤1输出数据验证"""
        output = AgentStep1Output(is_wait_for_login=True)
        assert output.is_wait_for_login is True

        # 测试默认值
        default_output = AgentStep1Output()
        assert default_output.is_wait_for_login is False

    @pytest.mark.asyncio
    async def test_step_agent_instance_init_empty_id(self):
        """测试空ID的错误处理"""
        from mtmai.flows.flow_agent import step_agent_instance_init

        # 创建模拟的Context
        mock_ctx = MagicMock()
        mock_ctx.log = MagicMock()

        # 测试空ID
        empty_input = FlowAgentInput(id="")

        with pytest.raises(ValueError, match="AgentId为空，无法启动napcat服务"):
            await step_agent_instance_init.fn(empty_input, mock_ctx)

    @pytest.mark.asyncio
    @patch("mtmai.flows.flow_agent.GomtmApiClient")
    async def test_step_agent_instance_init_success(self, mock_api_client_class):
        """测试智能体实例初始化成功流程"""
        from mtmai.flows.flow_agent import step_agent_instance_init

        # 创建模拟的Context
        mock_ctx = MagicMock()
        mock_ctx.log = MagicMock()

        # 创建模拟的API客户端
        mock_api_client = AsyncMock()
        mock_api_client.__aenter__ = AsyncMock(return_value=mock_api_client)
        mock_api_client.__aexit__ = AsyncMock(return_value=None)
        mock_api_client.get_agent = AsyncMock(
            return_value={"name": "chatbot", "state": {}}
        )
        mock_api_client.update_agent_state = AsyncMock()
        mock_api_client_class.return_value = mock_api_client

        # 创建模拟的沙盒管理器
        with patch("mtmai.flows.flow_agent.get_sandbox_manager") as mock_get_sandbox:
            mock_sandbox_manager = AsyncMock()
            mock_napcat_client = AsyncMock()
            mock_napcat_client.url = "http://test-napcat:3000"
            mock_napcat_client.get_qr_code_url = AsyncMock(
                return_value="http://test-qr.png"
            )
            mock_napcat_client.wait_qq_login = AsyncMock(return_value="123456789")

            mock_sandbox_manager.get_or_create_instance = AsyncMock(
                return_value=mock_napcat_client
            )
            mock_get_sandbox.return_value = mock_sandbox_manager

            # 测试输入
            test_input = FlowAgentInput(
                id="test-agent-123",
                mtmapi_url="https://api.example.com",
                mtmapi_api_token="test-token",
            )

            # 执行测试
            result = await step_agent_instance_init.fn(test_input, mock_ctx)

            # 验证结果
            assert isinstance(result, AgentStep1Output)
            assert result.is_wait_for_login is False

            # 验证API调用
            mock_api_client.get_agent.assert_called_once_with("test-agent-123")
            assert mock_api_client.update_agent_state.call_count >= 1

    def test_workflow_registration(self):
        """测试工作流注册"""
        from mtmai.flows.flow_agent import flow_agent

        # 验证工作流属性
        assert flow_agent.name == "agent-start-workflow"
        # 注意：hatchet SDK中的on_events可能不是直接属性

        # 验证工作流有正确的步骤
        assert len(flow_agent.tasks) >= 2  # 至少有两个步骤
