from typing import *

from pydantic import BaseModel, Field

from .MqMessage import MqMessage


class WorkerPullResp(BaseModel):
    """
    WorkerPullResp model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: Optional[str] = Field(validation_alias="error", default=None)

    data: List[MqMessage] = Field(validation_alias="data")
