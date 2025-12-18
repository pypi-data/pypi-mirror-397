from typing import *

from pydantic import BaseModel, Field


class WorkerAckResp(BaseModel):
    """
    WorkerAckResp model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: Optional[str] = Field(validation_alias="error", default=None)

    data: Optional[Any] = Field(validation_alias="data", default=None)
