from typing import *

from pydantic import BaseModel, Field


class BrowserDeleteReq(BaseModel):
    """
    BrowserDeleteReq model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: str = Field(validation_alias="id")
