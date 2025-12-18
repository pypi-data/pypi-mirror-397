from typing import *

from pydantic import BaseModel, Field


class AdkExecutableCode(BaseModel):
    """
    AdkExecutableCode model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    language: str = Field(validation_alias="language")

    code: str = Field(validation_alias="code")
