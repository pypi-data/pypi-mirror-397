import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class CredentialsData(BaseModel):
    """认证数据模型"""
    username: str
    password: str


class ClientConfig(BaseModel):
    """客户端配置模型"""
    server_url: str
    credentials: Optional[CredentialsData] = None


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.environ.get(
            "MTM_CREDENTIALS", "credentials.json"
        )
    
    def load_credentials(self) -> CredentialsData:
        """加载认证信息"""
        credentials_file = Path(self.credentials_path)
        
        if credentials_file.exists():
            with open(credentials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CredentialsData(**data)
        
        # 如果文件不存在，返回默认值
        return CredentialsData(
            username=os.environ.get("MTM_USERNAME", "admin@example.com"),
            password=os.environ.get("MTM_PASSWORD", "Admin123!!")
        )
    
    def load_client_config(self, config: ClientConfig) -> ClientConfig:
        """加载客户端配置"""
        if not config.credentials:
            config.credentials = self.load_credentials()
        return config
    
    def save_credentials(self, credentials: CredentialsData) -> None:
        """保存认证信息"""
        credentials_file = Path(self.credentials_path)
        credentials_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(credentials_file, 'w', encoding='utf-8') as f:
            json.dump(credentials.model_dump(), f, indent=2)
