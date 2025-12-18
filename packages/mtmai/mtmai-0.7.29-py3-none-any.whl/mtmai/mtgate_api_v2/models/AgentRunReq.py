from typing import *

from pydantic import BaseModel, Field

from .GenaiContent import GenaiContent


class AgentRunReq(BaseModel):
    """
    AgentRunReq model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    agentName: str = Field(validation_alias="agentName")

    newMessage: GenaiContent = Field(validation_alias="newMessage")

    sessionId: str = Field(validation_alias="sessionId")

    stateDelta: Optional[Any] = Field(validation_alias="stateDelta", default=None)

    streaming: Optional[bool] = Field(validation_alias="streaming", default=None)

    userId: Optional[str] = Field(validation_alias="userId", default=None)
