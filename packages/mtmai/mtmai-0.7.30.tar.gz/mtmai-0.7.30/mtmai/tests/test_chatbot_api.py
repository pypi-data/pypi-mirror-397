"""
测试chatbot API的基本功能
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from mtmai.api.chatbot import router
from mtmai.models.chatbot import Chatbot, ChatbotCreate, ChatbotUpdate


# 创建测试应用
app = FastAPI()
app.include_router(router)


def test_chatbot_models():
    """测试chatbot模型的基本功能"""
    # 测试创建模型
    create_data = ChatbotCreate(
        name="test_bot",
        description="测试机器人",
        config={"key": "value"}
    )
    assert create_data.name == "test_bot"
    assert create_data.description == "测试机器人"
    assert create_data.config == {"key": "value"}
    
    # 测试更新模型
    update_data = ChatbotUpdate(
        name="updated_bot",
        status="running"
    )
    assert update_data.name == "updated_bot"
    assert update_data.status == "running"
    assert update_data.description is None  # 未设置的字段应为None


def test_chatbot_database_model():
    """测试chatbot数据库模型"""
    tenant_id = uuid.uuid4()
    
    # 创建chatbot实例
    chatbot = Chatbot(
        name="test_bot",
        description="测试机器人",
        tenant_id=tenant_id,
        status="stopped",
        config={"protocol": "onebot11"},
        state={"is_running": False}
    )
    
    assert chatbot.name == "test_bot"
    assert chatbot.description == "测试机器人"
    assert chatbot.tenant_id == tenant_id
    assert chatbot.status == "stopped"
    assert chatbot.config == {"protocol": "onebot11"}
    assert chatbot.state == {"is_running": False}
    assert chatbot.deleted_at is None


def test_api_endpoints_structure():
    """测试API端点的基本结构"""
    client = TestClient(app)
    
    # 由于我们没有真实的数据库连接，这些测试会失败
    # 但我们可以验证路由是否正确注册
    
    # 检查路由是否存在
    routes = [route.path for route in app.routes]
    expected_routes = [
        "/chatbots/",
        "/chatbots/{chatbot_id}",
        "/chatbots/{chatbot_id}/start",
        "/chatbots/{chatbot_id}/stop"
    ]
    
    for expected_route in expected_routes:
        # 检查是否有匹配的路由模式
        route_exists = any(expected_route.replace("{chatbot_id}", "test-id") in route or 
                          expected_route in route for route in routes)
        assert route_exists, f"Route {expected_route} not found in {routes}"


if __name__ == "__main__":
    # 运行基本测试
    test_chatbot_models()
    test_chatbot_database_model()
    test_api_endpoints_structure()
    print("所有基本测试通过！")
