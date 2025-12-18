from typing import *

from pydantic import BaseModel, Field

from .AdkPart import AdkPart


class GenaiContent(BaseModel):
    """
    GenaiContent model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    role: str = Field(validation_alias="role")

    parts: List[AdkPart] = Field(validation_alias="parts")
