from typing import *

from pydantic import BaseModel, Field


class AuthMeResp(BaseModel):
    """
    AuthMeResp model
        AuthMeResp
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    uid: Optional[str] = Field(validation_alias="uid", default=None)
