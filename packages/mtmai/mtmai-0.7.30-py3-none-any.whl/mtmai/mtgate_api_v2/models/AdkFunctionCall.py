from typing import *

from pydantic import BaseModel, Field


class AdkFunctionCall(BaseModel):
    """
    AdkFunctionCall model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    name: str = Field(validation_alias="name")

    args: Dict[str, Any] = Field(validation_alias="args")
