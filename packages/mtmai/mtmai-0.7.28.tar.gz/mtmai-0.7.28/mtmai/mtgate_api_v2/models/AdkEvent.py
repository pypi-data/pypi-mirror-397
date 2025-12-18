from typing import *

from pydantic import BaseModel, Field

from .AdkEventActions import AdkEventActions
from .GenaiContent import GenaiContent


class AdkEvent(BaseModel):
    """
    AdkEvent model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    author: Optional[str] = Field(validation_alias="author", default=None)

    invocationId: Optional[str] = Field(validation_alias="invocationId", default=None)

    actions: Optional[AdkEventActions] = Field(validation_alias="actions", default=None)

    longRunningToolIds: Optional[List[str]] = Field(validation_alias="longRunningToolIds", default=None)

    branch: Optional[str] = Field(validation_alias="branch", default=None)

    timestamp: Optional[float] = Field(validation_alias="timestamp", default=None)

    content: Optional[GenaiContent] = Field(validation_alias="content", default=None)

    error: Optional[str] = Field(validation_alias="error", default=None)

    errorMessage: Optional[str] = Field(validation_alias="errorMessage", default=None)

    errorCode: Optional[str] = Field(validation_alias="errorCode", default=None)

    groundingMetadata: Optional[Any] = Field(validation_alias="groundingMetadata", default=None)

    usageMetadata: Optional[Any] = Field(validation_alias="usageMetadata", default=None)

    citationMetadata: Optional[Any] = Field(validation_alias="citationMetadata", default=None)

    customMetadata: Optional[Any] = Field(validation_alias="customMetadata", default=None)

    turnComplete: Optional[bool] = Field(validation_alias="turnComplete", default=None)

    interrupted: Optional[bool] = Field(validation_alias="interrupted", default=None)
