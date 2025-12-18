from typing import *

from pydantic import BaseModel, Field


class AgentQuickActionItem(BaseModel):
    """
    AgentQuickActionItem model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    icon: Optional[str] = Field(validation_alias="icon", default=None)

    text: str = Field(validation_alias="text")
