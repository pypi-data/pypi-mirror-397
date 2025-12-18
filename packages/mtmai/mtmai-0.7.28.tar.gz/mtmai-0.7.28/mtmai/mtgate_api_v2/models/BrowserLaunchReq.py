from typing import *

from pydantic import BaseModel, Field


class BrowserLaunchReq(BaseModel):
    """
    BrowserLaunchReq model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    browser_id: str = Field(validation_alias="browser_id")
