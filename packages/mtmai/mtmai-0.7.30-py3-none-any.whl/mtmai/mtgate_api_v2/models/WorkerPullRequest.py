from typing import *

from pydantic import BaseModel, Field


class WorkerPullRequest(BaseModel):
    """
    WorkerPullRequest model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    worker_id: str = Field(validation_alias="worker_id")
