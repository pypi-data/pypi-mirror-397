"""
AI模型配置管理模块
支持多种AI提供商的配置管理、验证和持久化存储
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

# import json
# import os
import yaml
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from mtmai.core.config import settings


class ModelProvider(BaseModel):
    """AI模型提供商配置"""

    name: str = Field(..., description="提供商名称")
    display_name: str = Field(..., description="显示名称")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    models: List[str] = Field(default_factory=list, description="支持的模型列表")
    enabled: bool = Field(True, description="是否启用")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("API密钥长度不能少于10个字符")
        return v


class AIConfig(BaseModel):
    """AI配置管理"""

    providers: Dict[str, ModelProvider] = Field(default_factory=dict)
    default_provider: str = Field("openai", description="默认提供商")
    default_model: str = Field("gpt-4o-mini", description="默认模型")
    max_turns: int = Field(10, description="最大对话轮次")
    system_message: str = Field(
        "你是一个有用的AI助手，可以回答各种问题并提供帮助。", description="系统消息"
    )

    def get_provider(self, name: str) -> Optional[ModelProvider]:
        return self.providers.get(name)

    def get_default_provider(self) -> Optional[ModelProvider]:
        return self.providers.get(self.default_provider)


class AIConfigManager:
    """AI配置管理器"""

    def __init__(self):
        self.config_file = Path(settings.storage_dir) / "ai_config.yaml"
        self._config: Optional[AIConfig] = None
        self._init_default_providers()

    def _init_default_providers(self):
        default_providers = {
            "openai": ModelProvider(
                name="openai",
                display_name="OpenAI",
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
                models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            ),
            "anthropic": ModelProvider(
                name="anthropic",
                display_name="Anthropic (Claude)",
                api_key=settings.ANTHROPIC_API_KEY,
                base_url=settings.ANTHROPIC_BASE_URL or "https://api.anthropic.com",
                models=[
                    "claude-3-5-sonnet-20241022",
                    "claude-3-opus-20240229",
                    "claude-3-haiku-20240307",
                ],
            ),
            "google": ModelProvider(
                name="google",
                display_name="Google AI Studio",
                api_key=settings.GOOGLE_AI_STUDIO_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            ),
            "openrouter": ModelProvider(
                name="openrouter",
                display_name="OpenRouter",
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                models=[
                    "anthropic/claude-3.5-sonnet",
                    "openai/gpt-4o",
                    "google/gemini-pro",
                ],
            ),
        }

        self._default_config = AIConfig(providers=default_providers)

    async def load_config(self) -> AIConfig:
        if self._config is not None:
            return self._config

        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self._config = AIConfig(**data)
                    logger.info(f"已加载AI配置: {self.config_file}")
            else:
                self._config = self._default_config
                await self.save_config()
                logger.info("使用默认AI配置")
        except Exception as e:
            logger.error(f"加载AI配置失败: {e}")
            self._config = self._default_config

        return self._config

    async def save_config(self) -> bool:
        try:
            if self._config is None:
                return False

            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            config_dict = self._config.model_dump()
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"AI配置已保存: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存AI配置失败: {e}")
            return False

    async def update_provider(
        self, provider_name: str, provider_config: Dict[str, Any]
    ) -> bool:
        try:
            config = await self.load_config()

            if provider_name in config.providers:
                provider = config.providers[provider_name]
                for key, value in provider_config.items():
                    if hasattr(provider, key):
                        setattr(provider, key, value)
            else:
                config.providers[provider_name] = ModelProvider(**provider_config)

            return await self.save_config()
        except Exception as e:
            logger.error(f"更新提供商配置失败: {e}")
            return False

    async def validate_api_key(
        self, provider_name: str, api_key: str, base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            config = await self.load_config()
            provider = config.get_provider(provider_name)

            if not provider:
                return {"valid": False, "error": "未知的提供商"}

            validators = {
                "openai": self._validate_openai_key,
                "anthropic": self._validate_anthropic_key,
                "google": self._validate_google_key,
            }

            validator = validators.get(provider_name, self._validate_generic_key)
            return await validator(api_key, base_url or provider.base_url)

        except Exception as e:
            logger.error(f"验证API密钥失败: {e}")
            return {"valid": False, "error": str(e)}

    async def _validate_openai_key(self, api_key: str, base_url: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{base_url}/models", headers={"Authorization": f"Bearer {api_key}"}
                )
                if response.status_code == 200:
                    return {"valid": True, "message": "API密钥验证成功"}
                else:
                    return {
                        "valid": False,
                        "error": f"验证失败: {response.status_code}",
                    }
        except Exception as e:
            return {"valid": False, "error": f"网络错误: {str(e)}"}

    async def _validate_anthropic_key(
        self, api_key: str, base_url: str
    ) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{base_url}/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "test"}],
                    },
                )
                if response.status_code in [200, 400]:
                    return {"valid": True, "message": "API密钥验证成功"}
                else:
                    return {
                        "valid": False,
                        "error": f"验证失败: {response.status_code}",
                    }
        except Exception as e:
            return {"valid": False, "error": f"网络错误: {str(e)}"}

    async def _validate_google_key(self, api_key: str, base_url: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}/models?key={api_key}")
                if response.status_code == 200:
                    return {"valid": True, "message": "API密钥验证成功"}
                else:
                    return {
                        "valid": False,
                        "error": f"验证失败: {response.status_code}",
                    }
        except Exception as e:
            return {"valid": False, "error": f"网络错误: {str(e)}"}

    async def _validate_generic_key(
        self, api_key: str, base_url: str
    ) -> Dict[str, Any]:
        if not api_key or len(api_key.strip()) < 10:
            return {"valid": False, "error": "API密钥格式不正确"}
        return {"valid": True, "message": "API密钥格式正确（未进行在线验证）"}

    async def export_config(self) -> Dict[str, Any]:
        config = await self.load_config()
        return config.model_dump()

    async def import_config(self, config_data: Dict[str, Any]) -> bool:
        try:
            self._config = AIConfig(**config_data)
            return await self.save_config()
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False


ai_config_manager = AIConfigManager()

ai_config_manager = AIConfigManager()
