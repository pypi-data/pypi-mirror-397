from typing import *

from pydantic import BaseModel, Field


class NstDocItem(BaseModel):
    """
    NstDocItem model
        NstDocItem
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    name: str = Field(validation_alias="name")

    profileId: str = Field(validation_alias="profileId")
