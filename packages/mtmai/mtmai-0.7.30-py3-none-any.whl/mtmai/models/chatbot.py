import uuid
from datetime import datetime
from typing import Literal, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from mtmai.models.base_model import MtmBaseSqlModel
from pydantic import BaseModel


# 聊天机器人状态枚举
ChatbotStatus = Literal["stopped", "starting", "waiting_login", "logging_in", "running", "error"]


class ChatbotBase(SQLModel):
    """聊天机器人基础模型"""
    name: str = Field(max_length=255, description="智能体名称")
    description: str = Field(default="", description="智能体描述")
    status: str = Field(default="stopped", description="智能体状态")
    tenant_id: uuid.UUID = Field(description="租户ID")


class Chatbot(ChatbotBase, MtmBaseSqlModel, table=True):
    """聊天机器人数据库模型"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="配置信息")
    state: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="状态信息")
    deleted_at: Optional[datetime] = Field(default=None, description="软删除时间")

    # class Config:
    #     table = True


class ChatbotCreate(BaseModel):
    """创建聊天机器人请求模型"""
    name: str = Field(max_length=255, description="智能体名称")
    description: str = Field(default="", description="智能体描述")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置信息")


class ChatbotUpdate(BaseModel):
    """更新聊天机器人请求模型"""
    name: Optional[str] = Field(default=None, max_length=255, description="智能体名称")
    description: Optional[str] = Field(default=None, description="智能体描述")
    status: Optional[ChatbotStatus] = Field(default=None, description="智能体状态")
    config: Optional[Dict[str, Any]] = Field(default=None, description="配置信息")
    state: Optional[Dict[str, Any]] = Field(default=None, description="状态信息")


class ChatbotResponse(BaseModel):
    """聊天机器人响应模型"""
    id: uuid.UUID
    name: str
    description: str
    status: ChatbotStatus
    tenant_id: uuid.UUID
    config: Dict[str, Any]
    state: Dict[str, Any]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ChatbotListResponse(BaseModel):
    """聊天机器人列表响应模型"""
    items: list[ChatbotResponse]
    total: int
    page: int
    limit: int
