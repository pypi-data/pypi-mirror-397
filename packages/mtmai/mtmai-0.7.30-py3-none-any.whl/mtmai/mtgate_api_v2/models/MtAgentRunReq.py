from typing import *

from pydantic import BaseModel, Field


class MtAgentRunReq(BaseModel):
    """
    MtAgentRunReq model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    agentName: Optional[str] = Field(validation_alias="agentName", default=None)

    messages: List[Any] = Field(validation_alias="messages")

    sessionId: Optional[str] = Field(validation_alias="sessionId", default=None)

    stateDelta: Optional[Any] = Field(validation_alias="stateDelta", default=None)

    streaming: Optional[bool] = Field(validation_alias="streaming", default=None)

    userId: Optional[str] = Field(validation_alias="userId", default=None)
