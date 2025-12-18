import asyncio
import unittest
import sys
import time
from typing import Any

from mtmai.mtlibs.py_sandbox import execute_python_code


class TestPySandbox:
    """
    py_sandbox 的测试集合。
    涵盖：同步/异步、上下文注入、库注入、错误处理、日志捕获、作用域隔离。
    """

    async def run_test(self, name: str, coro: Any):
        """简单的异步测试运行器辅助函数"""
        print(f"Testing: {name} ... ", end="")
        try:
            await coro
            print("PASS ✅")
        except AssertionError as e:
            print(f"FAIL ❌")
            print(f"   Assertion failed: {e}")
        except Exception as e:
            print(f"ERROR 💥")
            print(f"   Unexpected error: {e}")

    # --- 测试用例 ---

    async def test_01_basic_script(self):
        """测试基础脚本执行 (无 main 函数)"""
        code = """
print("Computing...")
result = 10 + 20
        """
        res = await execute_python_code(code)

        assert res["status"] == "success"
        assert res["result"] == 30
        assert "Computing..." in res["logs"]

    async def test_02_context_injection(self):
        """测试上下文变量注入 (Context)"""
        code = "result = user_id * 2"
        context = {"user_id": 100}

        res = await execute_python_code(code, context=context)

        assert res["result"] == 200

    async def test_03_dependency_injection(self):
        """测试第三方库/自定义库注入 (Extra Globals)"""

        # 模拟一个自定义库对象
        class MockLib:
            def get_data(self):
                return "data_from_lib"

        mock_lib = MockLib()

        code = """
val = mylib.get_data()
result = f"Got: {val}"
        """
        # 注入 mock_lib，在代码中名为 'mylib'
        extra_globals = {"mylib": mock_lib}

        res = await execute_python_code(code, extra_globals=extra_globals)

        assert res["result"] == "Got: data_from_lib"

    async def test_04_sync_main_function(self):
        """测试同步入口函数 (def main)"""
        code = """
def main():
    print("Inside main")
    return "returned_from_main"
        """
        res = await execute_python_code(code, entry_point="main")

        assert res["result"] == "returned_from_main"
        assert "Inside main" in res["logs"]

    async def test_05_async_main_function(self):
        """测试异步入口函数 (async def main) - 核心功能"""
        code = """
import asyncio

async def main():
    print("Start async")
    await asyncio.sleep(0.01) # 模拟 IO
    print("End async")
    return "async_success"
        """
        res = await execute_python_code(code, entry_point="main")

        assert res["status"] == "success"
        assert res["result"] == "async_success"
        assert "Start async" in res["logs"]

    async def test_06_scope_isolation_fix(self):
        """测试作用域修正 (Unified Scope)"""
        # 验证：顶层 import 的模块，在函数内部也能访问
        # 如果 globals != locals，这通常会报错 NameError
        code = """
import math

def main():
    # 尝试在函数内使用顶层导入的 math
    return math.sqrt(16)
        """
        res = await execute_python_code(code)

        assert res["status"] == "success"
        assert res["result"] == 4.0

    async def test_07_error_handling(self):
        """测试错误捕获"""
        code = """
def main():
    return 1 / 0
        """
        res = await execute_python_code(code)
        assert res["status"] == "error"
        assert "division by zero" in res["error"]
        assert "ZeroDivisionError" in res["traceback"]
        assert res["duration"] >= 0

    async def test_08_empty_code(self):
        """测试空代码处理"""
        res = await execute_python_code("")
        assert res["status"] == "success"
        assert "Warning" in res["logs"]


async def main_runner():
    tester = TestPySandbox()
    print("=== 开始运行 py_sandbox 测试用例 ===\n")

    await tester.run_test("01_Basic_Script", tester.test_01_basic_script())
    await tester.run_test("02_Context_Injection", tester.test_02_context_injection())
    await tester.run_test(
        "03_Dependency_Injection", tester.test_03_dependency_injection()
    )
    await tester.run_test("04_Sync_Main", tester.test_04_sync_main_function())
    await tester.run_test("05_Async_Main", tester.test_05_async_main_function())
    await tester.run_test("06_Scope_Isolation", tester.test_06_scope_isolation_fix())
    await tester.run_test("07_Error_Handling", tester.test_07_error_handling())
    await tester.run_test("08_Empty_Code", tester.test_08_empty_code())

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main_runner())
