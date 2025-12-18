from typing import *

from pydantic import BaseModel, Field


class WorkerUpResp(BaseModel):
    """
    WorkerUpResp model
        WorkerUpResp
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    workerId: str = Field(validation_alias="workerId")

    supabase: Dict[str, Any] = Field(validation_alias="supabase")

    tunnel: Dict[str, Any] = Field(validation_alias="tunnel")

    services: Dict[str, Any] = Field(validation_alias="services")
