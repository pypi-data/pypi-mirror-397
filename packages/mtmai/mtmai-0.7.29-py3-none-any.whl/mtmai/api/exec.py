from typing import Any, Dict, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from mtmai.mtlibs.py_sandbox import execute_python_code

router = APIRouter()


class CodeRequest(BaseModel):
    code: str = Field(
        title="Python Code",
        description="要执行的 Python 源码。支持同步或异步(async def main)。",
        examples=["import asyncio\nasync def main():\n    return 'Hello from Agent'"],
    )

    context: Optional[Dict[str, Any]] = Field(
        default=None,
        title="Context Variables",
        description="注入到代码执行环境中的变量字典。",
        examples=[{"user_id": 1001, "query": "latest sales"}],
    )

class ExecResponse(BaseModel):
    status: str = Field(..., description="执行状态: 'success' 或 'error'")
    result: Optional[Any] = Field(
        None, description="代码执行结果 (main函数返回值 或 result变量)"
    )
    logs: str = Field("", description="标准输出 (print) 捕获的内容")
    error: Optional[str] = Field(None, description="错误摘要")
    traceback: Optional[str] = Field(None, description="完整的错误堆栈")
    duration: float = Field(0.0, description="执行耗时(秒)")


@router.post(
    "/exec",
    response_model=ExecResponse,
    summary="动态执行 Python 代码 (AI Agent)",
    description="在受限的软沙盒环境中执行 Python 代码。支持 async/await、多线程及预置的 Numpy/Pandas 环境。",
)
async def exec_python_post(req: CodeRequest):
    return await execute_python_code(
        code=req.code,
        context=req.context,
    )
