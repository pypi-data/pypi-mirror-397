from typing import *

from pydantic import BaseModel, Field


class BrowserLaunchResp(BaseModel):
    """
    BrowserLaunchResp model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    success: bool = Field(validation_alias="success")

    vnc_url: Optional[str] = Field(validation_alias="vnc_url", default=None)
