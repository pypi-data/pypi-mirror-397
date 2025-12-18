from typing import *

from pydantic import BaseModel, Field


class AdkFunctionResp(BaseModel):
    """
    AdkFunctionResp model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    name: str = Field(validation_alias="name")

    response: Dict[str, Any] = Field(validation_alias="response")
