from typing import *

from pydantic import BaseModel, Field


class BrowserCreateReq(BaseModel):
    """
    BrowserCreateReq model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    title: str = Field(validation_alias="title")

    description: Optional[str] = Field(validation_alias="description", default=None)

    profile_id: Optional[str] = Field(validation_alias="profile_id", default=None)

    provider: Optional[str] = Field(validation_alias="provider", default=None)

    provider_config: Optional[Any] = Field(validation_alias="provider_config", default=None)

    config: Optional[Any] = Field(validation_alias="config", default=None)
