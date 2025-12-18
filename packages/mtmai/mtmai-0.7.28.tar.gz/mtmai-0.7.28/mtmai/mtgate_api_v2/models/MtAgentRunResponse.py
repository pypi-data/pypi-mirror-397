from typing import *

from pydantic import BaseModel, Field


class MtAgentRunResponse(BaseModel):
    """
    MtAgentRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
