from typing import *

from pydantic import BaseModel, Field


class BrowserRow(BaseModel):
    """
    BrowserRow model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")

    created_at: str = Field(validation_alias="created_at")

    updated_at: str = Field(validation_alias="updated_at")

    title: Optional[str] = Field(validation_alias="title", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    profile_id: Optional[str] = Field(validation_alias="profile_id", default=None)

    provider: Optional[str] = Field(validation_alias="provider", default=None)

    provider_config: Optional[Any] = Field(validation_alias="provider_config", default=None)

    config: Optional[Any] = Field(validation_alias="config", default=None)

    sandbox_id: Optional[str] = Field(validation_alias="sandbox_id", default=None)

    vnc_url: Optional[str] = Field(validation_alias="vnc_url", default=None)

    worker_name: Optional[str] = Field(validation_alias="worker_name", default=None)

    is_running: Optional[bool] = Field(validation_alias="is_running", default=None)
