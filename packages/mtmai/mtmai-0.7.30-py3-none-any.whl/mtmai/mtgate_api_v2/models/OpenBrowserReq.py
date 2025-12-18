from typing import *

from pydantic import BaseModel, Field


class OpenBrowserReq(BaseModel):
    """
    OpenBrowserReq model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    url: str = Field(validation_alias="url")
