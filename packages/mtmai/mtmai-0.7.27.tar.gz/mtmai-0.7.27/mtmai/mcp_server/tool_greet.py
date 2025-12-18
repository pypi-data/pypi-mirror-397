from .mcp_app import mcpApp


@mcpApp.tool()
def greet(name: str) -> str:
    """
    向用户问候
    """
    return f"Hello, {name}!"


@mcpApp.tool()
def search_file(name: str) -> str:
    """
    搜索文件
    """
    return "not found"
