from typing import *

from pydantic import BaseModel, Field


class AdkBlob(BaseModel):
    """
    AdkBlob model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    mimeType: Optional[str] = Field(validation_alias="mimeType", default=None)

    data: str = Field(validation_alias="data")
