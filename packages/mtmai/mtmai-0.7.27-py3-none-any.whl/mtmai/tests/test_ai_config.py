"""
测试AI配置管理功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from mtmai.core.ai_config import AIConfigManager, AIConfig, ModelProvider


@pytest.fixture
def temp_config_manager():
    """创建临时配置管理器"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 临时修改存储目录
        original_storage_dir = os.environ.get("MTMAI_STORAGE_DIR")
        os.environ["MTMAI_STORAGE_DIR"] = temp_dir
        
        manager = AIConfigManager()
        manager.config_file = Path(temp_dir) / "test_ai_config.yaml"
        
        yield manager
        
        # 恢复原始环境变量
        if original_storage_dir:
            os.environ["MTMAI_STORAGE_DIR"] = original_storage_dir
        elif "MTMAI_STORAGE_DIR" in os.environ:
            del os.environ["MTMAI_STORAGE_DIR"]


@pytest.mark.asyncio
async def test_load_default_config(temp_config_manager):
    """测试加载默认配置"""
    config = await temp_config_manager.load_config()
    
    assert isinstance(config, AIConfig)
    assert "openai" in config.providers
    assert "anthropic" in config.providers
    assert "google" in config.providers
    assert config.default_provider == "openai"
    assert config.default_model == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_save_and_load_config(temp_config_manager):
    """测试保存和加载配置"""
    # 加载默认配置
    config = await temp_config_manager.load_config()
    
    # 修改配置
    config.default_model = "gpt-4o"
    config.max_turns = 20
    
    # 保存配置
    success = await temp_config_manager.save_config()
    assert success
    
    # 重新创建管理器并加载配置
    new_manager = AIConfigManager()
    new_manager.config_file = temp_config_manager.config_file
    new_config = await new_manager.load_config()
    
    assert new_config.default_model == "gpt-4o"
    assert new_config.max_turns == 20


@pytest.mark.asyncio
async def test_update_provider(temp_config_manager):
    """测试更新提供商配置"""
    # 更新OpenAI提供商配置
    success = await temp_config_manager.update_provider("openai", {
        "name": "openai",
        "api_key": "test-api-key",
        "base_url": "https://api.openai.com/v1"
    })
    assert success
    
    # 验证更新
    config = await temp_config_manager.load_config()
    openai_provider = config.get_provider("openai")
    assert openai_provider is not None
    assert openai_provider.api_key == "test-api-key"


@pytest.mark.asyncio
async def test_export_import_config(temp_config_manager):
    """测试配置导入导出"""
    # 加载并修改配置
    config = await temp_config_manager.load_config()
    config.default_model = "claude-3-5-sonnet-20241022"
    await temp_config_manager.save_config()
    
    # 导出配置
    exported_config = await temp_config_manager.export_config()
    assert exported_config["default_model"] == "claude-3-5-sonnet-20241022"
    
    # 创建新的管理器并导入配置
    new_manager = AIConfigManager()
    new_manager.config_file = Path(temp_config_manager.config_file.parent) / "new_config.yaml"
    
    success = await new_manager.import_config(exported_config)
    assert success
    
    # 验证导入的配置
    imported_config = await new_manager.load_config()
    assert imported_config.default_model == "claude-3-5-sonnet-20241022"


def test_model_provider_validation():
    """测试模型提供商验证"""
    # 测试有效的API密钥
    provider = ModelProvider(
        name="test",
        display_name="Test Provider",
        api_key="valid-api-key-123456",
        models=["test-model"]
    )
    assert provider.api_key == "valid-api-key-123456"
    
    # 测试无效的API密钥（太短）
    with pytest.raises(ValueError, match="API密钥长度不能少于10个字符"):
        ModelProvider(
            name="test",
            display_name="Test Provider",
            api_key="short",
            models=["test-model"]
        )


@pytest.mark.asyncio
async def test_get_provider_methods(temp_config_manager):
    """测试获取提供商的方法"""
    config = await temp_config_manager.load_config()
    
    # 测试获取指定提供商
    openai_provider = config.get_provider("openai")
    assert openai_provider is not None
    assert openai_provider.name == "openai"
    
    # 测试获取不存在的提供商
    unknown_provider = config.get_provider("unknown")
    assert unknown_provider is None
    
    # 测试获取默认提供商
    default_provider = config.get_default_provider()
    assert default_provider is not None
    assert default_provider.name == config.default_provider


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
