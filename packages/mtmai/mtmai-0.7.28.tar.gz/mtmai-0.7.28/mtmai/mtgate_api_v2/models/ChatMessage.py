from typing import *

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    ChatMessage model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    chat_id: str = Field(validation_alias="chat_id")

    role: str = Field(validation_alias="role")

    parts: Any = Field(validation_alias="parts")

    attachments: Any = Field(validation_alias="attachments")

    user_id: str = Field(validation_alias="user_id")
