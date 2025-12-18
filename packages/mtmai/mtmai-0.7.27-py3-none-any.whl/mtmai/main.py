import asyncio
import json
import os
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from mtmai.core.config import settings
from mtmai.mtmai_app import app
from mtmai.worker_main import MtWorker


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        ctx.invoke(serve)


@app.command()
def version():
    from ._version import __version__

    print(__version__)


@app.command()
def serve(
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Host to bind the server to"),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to bind the server to"),
    ] = settings.PORT,
    enable_worker: Annotated[
        bool,
        typer.Option("--enable-worker", "-w", help="Enable worker"),
    ] = True,
):
    from mtmai.server import MtmaiServeOptions, serve

    asyncio.run(
        serve(
            MtmaiServeOptions(
                host=host,
                port=port,
                enable_worker=enable_worker,
            )
        )
    )


async def start_chrome_server():
    cmd = (
        "google-chrome "
        "--remote-debugging-port=15001 "
        "--disable-dev-shm-usage "
        "--no-first-run "
        "--no-default-browser-check "
        "--disable-infobars "
        "--window-position=0,0 "
        "--disable-session-crashed-bubble "
        "--hide-crash-restore-bubble "
        "--disable-blink-features=AutomationControlled "
        "--disable-automation "
        "--disable-webgl "
        "--disable-webgl2"
    )
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        print("Chrome debugging server started on port 15001. Press Ctrl+C to exit...")
        await process.communicate()
    except KeyboardInterrupt:
        print("\nReceived Ctrl+C, shutting down Chrome...")
        process.terminate()
        await process.wait()


@app.command()
def mcpserver():
    import asyncio

    from mtmai.mcp_server.mcp_app import mcpApp

    logger.info(f"Starting MCP server on http://localhost:{settings.PORT}")
    asyncio.run(
        mcpApp.run_sse_async(
            host="0.0.0.0",
            port=settings.PORT,
        )
    )


@app.command()
def setup():
    os.system("sudo apt install -yqq ffmpeg imagemagick")
    os.system("apt-get install -y libpq-dev")
    # 修正 ImageMagick 安全策略, 允许读写
    cmd = "sudo sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml"
    os.system(cmd)

    commamd_line = """
uv sync --no-cache
# 原因: crawl4ai 库本本项目有冲突,所以使用独立的方式设置
uv pip install crawl4ai f2 --no-deps

# 原因: moviepy 库 引用了  pillow <=11
uv pip install "moviepy>=2.1.2" --no-deps
uv pip install "instagrapi>=2.1.3"

uv add playwright_stealth

uv pip install google-generativeai~=0.8.3
uv pip install torch
uv sync --no-cache
"""
    os.system(commamd_line)

    os.system("uv pip install litellm[proxy] --no-deps")


@app.command()
def setup_dev():
    # os.system(
    #     "uv pip install --no-cache git+https://github.com/google/adk-python.git@main"
    # )
    os.system("uv sync --no-cache --all-groups")
    os.system("uv pip install --no-cache lamda[full] --no-deps")


@app.command()
def download_models():
    from mtmai.mtlibs.hf_utils.hf_utils import download_whisper_model

    current_dir = os.path.dirname(os.path.abspath(__file__))
    download_whisper_model(
        os.path.join(current_dir, "mtlibs/NarratoAI/app/models/faster-whisper-large-v2")
    )


@app.command()
def gen_openapi():
    from .server import build_app
    # from pathlib import Path

    app = build_app()
    doc_spec = app.openapi()

    openapiOutputJsonFile = Path(os.path.abspath(os.path.dirname(__file__))).joinpath(
        "../packages/mtmsdk/openapi_mtmai.json"
    )
    # file_path = Path("./openapi_mtmai.json")
    print(openapiOutputJsonFile)
    with open(openapiOutputJsonFile, "w") as f:
        json.dump(doc_spec, f, indent=2)


@app.command()
def litellm():
    # 启动 litellm 代理
    # from litellm.proxy import proxy_cli
    # proxy_cli.run_server()
    os.system("uv tool install 'litellm[proxy]'")
    # os.system("uv pip install prisma psycopg2-binary")
    os.system(
        "python -m prisma generate --schema .venv/lib/python3.12/site-packages/litellm/proxy/schema.prisma"
    )
    os.system("uv run litellm --config='litellm_config.yaml'")


@app.command()
def run_short():
    from mtmai.flows.flow_videogen import ShortVideoGenInput, short_video_gen_workflow

    async def run_task():
        result = await short_video_gen_workflow.aio_run(
            input=ShortVideoGenInput(topic="动物世界的狂欢")
        )
        print(
            "任务结果: ",
            result,
        )

    asyncio.run(run_task())


@app.command()
def inst_register():
    from mtmai.mtlibs.instagram_utils.inst_register import main

    main()


@app.command()
def inst_rpa():
    from mtmai.rpa.inst_rpa import InstagramAutomation

    asyncio.run(InstagramAutomation("http://mtw-default-default:65000").start())


@app.command()
def supabase():
    from mtmai import supabase_demo

    asyncio.run(supabase_demo.realtime_demo())


@app.command()
def worker(
    env_file: Annotated[
        str,
        typer.Option("--env-file", "-e", help="Path to .env file"),
    ] = "env/dev.env",
):
    """Start the distributed worker to consume tasks from MtGate."""
    from dotenv import load_dotenv
    import socket

    load_dotenv(env_file)

    base_url = os.getenv("MTGATE_API_URL", "https://mtgateapi.yuepa8.com")
    hostname = socket.gethostname()
    worker_id = f"py-worker-{hostname}"

    worker = MtWorker(base_url=base_url, worker_id=worker_id)
    asyncio.run(worker.start())


if __name__ == "__main__":
    app()
    # typer.run(main)
