from typing import *

from pydantic import BaseModel, Field


class WorkerAckRequest(BaseModel):
    """
    WorkerAckRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    msg_id: float = Field(validation_alias="msg_id")
