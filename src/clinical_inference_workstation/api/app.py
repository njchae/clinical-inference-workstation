from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from clinical_inference_workstation.api.router import router
from clinical_inference_workstation.config import ROOT_DIR


def create_app() -> FastAPI:
    app = FastAPI(
        title="Clinical Inference Workstation",
        description=(
            "Public clinical inference workstation showcasing hybrid feature extraction, "
            "thresholding, and deployable inference."
        ),
        version="0.1.0",
    )
    web_dir = ROOT_DIR / "web"

    @app.middleware("http")
    async def attach_request_id(request, call_next):  # type: ignore[no-untyped-def]
        request.state.request_id = request.headers.get("X-Request-ID", uuid4().hex)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    app.include_router(router)
    app.mount("/workstation", StaticFiles(directory=web_dir), name="workstation")

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/workstation/index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:
        return FileResponse(web_dir / "samples" / "favicon.txt", media_type="text/plain")

    return app
