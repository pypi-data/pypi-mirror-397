from typing import *

from pydantic import BaseModel, Field


class AuthLoginResp(BaseModel):
    """
    AuthLoginResp model
        AuthLoginResp
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    paginate: Dict[str, Any] = Field(validation_alias="paginate")
