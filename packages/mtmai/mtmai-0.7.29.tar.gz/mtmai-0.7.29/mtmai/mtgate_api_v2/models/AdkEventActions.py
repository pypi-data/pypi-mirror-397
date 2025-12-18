from typing import *

from pydantic import BaseModel, Field

from .AdkFunctionCall import AdkFunctionCall
from .AdkFunctionResp import AdkFunctionResp


class AdkEventActions(BaseModel):
    """
    AdkEventActions model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    message: Optional[str] = Field(validation_alias="message", default=None)

    artifactDelta: Optional[Any] = Field(validation_alias="artifactDelta", default=None)

    functionCall: Optional[AdkFunctionCall] = Field(validation_alias="functionCall", default=None)

    functionResponse: Optional[AdkFunctionResp] = Field(validation_alias="functionResponse", default=None)

    finishReason: Optional[str] = Field(validation_alias="finishReason", default=None)
