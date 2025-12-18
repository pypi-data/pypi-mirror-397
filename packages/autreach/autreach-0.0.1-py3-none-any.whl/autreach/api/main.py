import socket
from importlib.metadata import version

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from autreach.api.common.constants import PROJECT_TITLE
from autreach.api.common.logger import logger, setup_logging
from autreach.api.common.utils.exception_handlers import register_exception_handlers
from autreach.api.common.utils.static_files import get_static_dir, serve_index_html


def create_app() -> FastAPI:
    setup_logging()

    app_version = version("autreach")

    app: FastAPI = FastAPI(
        title=PROJECT_TITLE,
        servers=[
            {
                "url": "http://127.0.0.1:8000",
                "description": "Local Development Server",
            },
        ],
        summary="Autreach API",
        description="Automate LinkedIn job discovery and personalized outreach with a real-time control dashboard.",
        version=app_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    static_dir = get_static_dir()
    if static_dir and (static_dir / "assets").exists():
        app.mount(
            "/assets",
            StaticFiles(directory=str(static_dir / "assets")),
            name="assets",
        )

    return app


# ========== FAST API APPLICATION ==========
app: FastAPI = create_app()

STATIC_DIR = get_static_dir()


@app.get("/")
async def root():
    return serve_index_html(STATIC_DIR)


@app.get("/health")
@app.get("/healthz")
async def health_check() -> JSONResponse:
    logger.info("Server is Healthy")
    return JSONResponse(
        content={
            "status": "ok",
            "hostname": socket.gethostname(),
            "version": app.version,
        }
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if STATIC_DIR and (STATIC_DIR / "favicon.ico").exists():
        return FileResponse(str(STATIC_DIR / "favicon.ico"))
    return Response(status_code=204)


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(request: Request, path: str):
    if path.startswith(("api/", "health", "healthz", "docs", "openapi.json", "redoc")):
        return Response(status_code=404)
    if STATIC_DIR:
        file_path = STATIC_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
    return serve_index_html(STATIC_DIR)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
