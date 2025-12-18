import uvicorn
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from loguru import logger
from pydantic import BaseModel

from mtmai.otel import setup_instrumentor


class MtmaiServeOptions(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    enable_worker: bool = True


def mount_api_routes(app: FastAPI, prefix="/api/mtmai"):
    # from mtmai.api import chat_agent, tiktok_api

    # app.include_router(tiktok_api.router, prefix=prefix, tags=["tiktok_api"])
    # app.include_router(chat_agent.router, prefix=f"{prefix}/chat", tags=["chat_agent"])
    from mtmai.api import items

    app.include_router(items.router)
    # 设置基于 fastapi 的 routes 结束
    from mtmai.api import home

    app.include_router(home.router)
    from mtmai.api import agent

    app.include_router(agent.router, prefix=f"{prefix}/agents", tags=["agents"])
    from mtmai.api import sandbox

    app.include_router(sandbox.router, prefix=f"{prefix}/sandbox", tags=["sandbox"])

    from mtmai.api import exec

    app.include_router(exec.router, prefix=f"{prefix}/exec", tags=["exec"])


def build_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        except Exception as e:
            logger.exception(f"failed to setup lifespan: {e}")

    def custom_generate_unique_id(route: APIRoute) -> str:
        if len(route.tags) > 0:
            return f"{route.tags[0]}-{route.name}"
        return f"{route.name}"

    from mtmai.cli.fast_api import get_fast_api_app

    app = get_fast_api_app(
        agents_dir="mtmai/agents",
        web=True,
        a2a=True,
        lifespan=lifespan,
    )
    mount_api_routes(app)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):  # noqa: ARG001
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    # if settings.OTEL_ENABLED:
    # from mtmai.mtlibs import otel

    # otel.setup_otel(app)

    # 启用CORS中间件以支持跨域请求
    from mtmai.core.config import Settings

    settings = Settings()

    if settings.BACKEND_CORS_ORIGINS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"]
            if settings.BACKEND_CORS_ORIGINS == "*"
            else [str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*", "x-chainlit-client-type"],
        )
    return app


async def serve(options: MtmaiServeOptions):
    setup_instrumentor()
    app = build_app()
    config = uvicorn.Config(
        app,
        host=options.host,
        port=options.port,
        log_level="info",
    )
    host = "127.0.0.1" if options.host == "0.0.0.0" else options.host.split("://")[-1]

    server = uvicorn.Server(config)

    logger.info(
        "server starting",
        host=options.host,
        port=options.port,
        server_url=f"{options.host.split('://')[0]}://{host}:{options.port}",
    )
    await server.serve()
