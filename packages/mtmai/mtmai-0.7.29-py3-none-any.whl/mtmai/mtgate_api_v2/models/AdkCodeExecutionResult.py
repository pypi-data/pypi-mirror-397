from typing import *

from pydantic import BaseModel, Field


class AdkCodeExecutionResult(BaseModel):
    """
    AdkCodeExecutionResult model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    outcome: str = Field(validation_alias="outcome")

    output: str = Field(validation_alias="output")
