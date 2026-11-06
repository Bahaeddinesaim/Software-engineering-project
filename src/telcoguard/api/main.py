"""FastAPI application factory with explicit artifact lifecycle."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from telcoguard.api.routes import router
from telcoguard.config import Settings
from telcoguard.ml.inference import Predictor

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an app that remains diagnosable when trusted artifacts are missing."""
    configuration = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
        logger.info("application_starting")
        app.state.settings = configuration
        app.state.predictor = None
        try:
            app.state.predictor = Predictor(configuration.model_path)
            logger.info("model_loaded")
        except Exception:
            logger.error("model_unavailable")
        yield
        logger.info("application_stopped")

    app = FastAPI(title="TelcoGuard AI", version="1.0.0", lifespan=lifespan)
    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def validation_failure(request: Request, error: RequestValidationError):
        logger.warning("request_validation_failed")
        # Do not echo request values or validation contexts containing private data.
        details = [
            {"loc": list(item["loc"]), "msg": item["msg"], "type": item["type"]}
            for item in error.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": details})

    return app


app = create_app()
