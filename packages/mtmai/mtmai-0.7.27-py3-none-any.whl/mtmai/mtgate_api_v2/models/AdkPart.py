from typing import *

from pydantic import BaseModel, Field

from .AdkBlob import AdkBlob
from .AdkCodeExecutionResult import AdkCodeExecutionResult
from .AdkExecutableCode import AdkExecutableCode
from .AdkFileData import AdkFileData
from .AdkFunctionCall import AdkFunctionCall
from .AdkFunctionResp import AdkFunctionResp


class AdkPart(BaseModel):
    """
    AdkPart model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    text: Optional[str] = Field(validation_alias="text", default=None)

    inlineData: Optional[AdkBlob] = Field(validation_alias="inlineData", default=None)

    functionCall: Optional[AdkFunctionCall] = Field(validation_alias="functionCall", default=None)

    functionResponse: Optional[AdkFunctionResp] = Field(validation_alias="functionResponse", default=None)

    thought: Optional[bool] = Field(validation_alias="thought", default=None)

    fileData: Optional[AdkFileData] = Field(validation_alias="fileData", default=None)

    executableCode: Optional[AdkExecutableCode] = Field(validation_alias="executableCode", default=None)

    codeExecutionResult: Optional[AdkCodeExecutionResult] = Field(validation_alias="codeExecutionResult", default=None)
