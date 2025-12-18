from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ChatMessage(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: str  # 'user' | 'assistant' | 'system'
    # 兼容数据库返回可能是 None 的情况
    parts: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

    @field_validator("parts", mode="before")
    def parse_parts(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # 某些情况下驱动可能返回 json 字符串
            import json

            try:
                return json.loads(v)
            except:
                return []
        return v

    @property
    def text_content(self) -> str:
        """提取纯文本内容，用于 Prompt 拼接"""
        text = ""
        for part in self.parts:
            if "text" in part:
                text += part["text"]
        return text


class ChatHistory(BaseModel):
    messages: List[ChatMessage]
