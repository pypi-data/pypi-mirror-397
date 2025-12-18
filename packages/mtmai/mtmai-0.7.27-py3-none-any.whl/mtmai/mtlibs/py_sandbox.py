import inspect
import io
import time
import traceback
import asyncio
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


async def execute_python_code(
    code: str,
    context: Optional[Dict[str, Any]] = None,
    extra_globals: Optional[Dict[str, Any]] = None,
    entry_point: str = "main",
) -> Dict[str, Any]:
    """
    【高并发修正版】在软沙盒中动态执行 Python 代码。
    """

    # 1. 基础校验
    if not code or not code.strip():
        return {
            "status": "success",
            "result": None,
            "logs": "Warning: Empty code provided.",
            "duration": 0.0,
        }

    # 2. 准备输出捕获
    # 每个请求拥有独立的 Buffer
    stdout_capture = io.StringIO()

    # --- 自定义 print 函数 (线程安全的核心) ---
    # 我们不修改全局 sys.stdout，而是给一个专属的 print
    def safe_print(*args, sep=" ", end="\n", file=None, flush=False):
        # 强制将输出写入当前的 stdout_capture，忽略 file 参数
        print(*args, sep=sep, end=end, file=stdout_capture, flush=flush)

    # 3. 准备沙箱环境
    sandbox = {
        "__builtins__": __builtins__.copy(),  # 浅拷贝，防止修改原生命名空间
        "print": safe_print,
    }

    # 移除 sandbox 里可能存在的危险/干扰函数 (可选)
    # sandbox["__builtins__"].pop('open', None)
    # sandbox["__builtins__"].pop('exit', None)

    if extra_globals:
        sandbox.update(extra_globals)
    if context:
        sandbox.update(context)

    start_time = time.perf_counter()

    try:
        # --- 核心优化：在线程池中运行 exec ---
        await asyncio.to_thread(exec, code, sandbox, sandbox)
        result = None
        if entry_point in sandbox and callable(sandbox[entry_point]):
            func = sandbox[entry_point]

            # 情况 A: 异步入口 (async def main)
            # 必须在主线程 await，不能在线程池里跑
            if inspect.iscoroutinefunction(func):
                result = await func()

            # 情况 B: 同步入口 (def main)
            # 如果这是个耗时计算，必须放到线程池里跑，否则依然卡死主线程
            else:
                result = await asyncio.to_thread(func)
        else:
            # 兼容脚本模式
            result = sandbox.get("result", None)

        duration = time.perf_counter() - start_time

        return {
            "status": "success",
            "result": result,
            "logs": stdout_capture.getvalue(),
            "duration": duration,
        }

    except Exception as e:
        duration = time.perf_counter() - start_time
        error_msg = str(e)
        tb_str = traceback.format_exc()

        # 记录简要日志
        logger.error(f"Sandbox Exec Error: {error_msg}")

        return {
            "status": "error",
            "error": error_msg,
            "traceback": tb_str,
            "result": None,
            "logs": stdout_capture.getvalue(),
            "duration": duration,
        }
