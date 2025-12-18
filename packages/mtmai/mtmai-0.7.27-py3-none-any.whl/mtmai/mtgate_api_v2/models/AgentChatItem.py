from typing import *

from pydantic import BaseModel, Field


class AgentChatItem(BaseModel):
    """
    AgentChatItem model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    title: str = Field(validation_alias="title")

    user_id: str = Field(validation_alias="user_id")

    visibility: str = Field(validation_alias="visibility")

    lastContext: Optional[Any] = Field(validation_alias="lastContext", default=None)

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")
