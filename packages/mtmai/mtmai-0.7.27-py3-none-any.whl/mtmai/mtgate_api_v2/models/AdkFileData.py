from typing import *

from pydantic import BaseModel, Field


class AdkFileData(BaseModel):
    """
    AdkFileData model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    mimeType: str = Field(validation_alias="mimeType")

    fileUri: str = Field(validation_alias="fileUri")
