from typing import *

from pydantic import BaseModel, Field


class WorkerUpRequest(BaseModel):
    """
    WorkerUpRequest model
        WorkerUpRequest
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    workerId: Optional[str] = Field(validation_alias="workerId", default=None)

    botType: Optional[str] = Field(validation_alias="botType", default=None)
