from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


def tool_success(data: dict[str, Any] | str | BaseModel | None):
    if data is None:
        return {"success": False}

    result = data
    if isinstance(data, BaseModel):
        result = jsonable_encoder(data.model_dump())

    return {"success": True, "result": result}
