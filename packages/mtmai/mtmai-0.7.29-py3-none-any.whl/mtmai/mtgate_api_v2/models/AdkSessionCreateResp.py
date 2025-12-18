from typing import *

from pydantic import BaseModel, Field


class AdkSessionCreateResp(BaseModel):
    """
    AdkSessionCreateResp model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: Optional[str] = Field(validation_alias="error", default=None)

    data: Optional[Dict[str, Any]] = Field(validation_alias="data", default=None)
