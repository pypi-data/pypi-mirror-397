from typing import *

from pydantic import BaseModel, Field


class BrowserCreateResult(BaseModel):
    """
    BrowserCreateResult model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    title: Optional[str] = Field(validation_alias="title", default=None)

    created_at: Optional[str] = Field(validation_alias="created_at", default=None)

    provider: Optional[str] = Field(validation_alias="provider", default=None)
