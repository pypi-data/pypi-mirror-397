from typing import *

from pydantic import BaseModel, Field


class MqMessage(BaseModel):
    """
    MqMessage model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    msg_id: float = Field(validation_alias="msg_id")

    read_ct: float = Field(validation_alias="read_ct")

    enqueued_at: Optional[str] = Field(validation_alias="enqueued_at", default=None)

    message: Any = Field(validation_alias="message")
