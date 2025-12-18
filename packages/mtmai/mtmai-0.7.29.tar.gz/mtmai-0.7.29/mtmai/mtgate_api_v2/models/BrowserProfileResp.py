from typing import *

from pydantic import BaseModel, Field


class BrowserProfileResp(BaseModel):
    """
    BrowserProfileResp model
        BrowserProfileResponse
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    data: Dict[str, Any] = Field(validation_alias="data")
