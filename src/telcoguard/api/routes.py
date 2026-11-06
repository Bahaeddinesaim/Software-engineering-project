"""Health and prediction endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from telcoguard.api.dependencies import require_api_key
from telcoguard.api.schemas import Customer, Prediction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health(request: Request):
    """Return 503 until both the model and authentication are available."""
    loaded = request.app.state.predictor is not None
    ready = loaded and request.app.state.settings.api_key is not None
    return JSONResponse(
        {"status": "healthy" if ready else "unavailable", "model_loaded": loaded},
        status_code=200 if ready else 503,
    )


@router.post("/predict", response_model=Prediction)
def predict(
    customer: Customer, request: Request, authenticated: Annotated[None, Depends(require_api_key)]
):
    """Predict one customer; payloads, credentials and identifiers are never logged."""
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(503, "Model is unavailable")
    try:
        result = predictor.predict(customer.model_dump(), request.app.state.settings.threshold)
        validated = Prediction.model_validate(result)
    except Exception:
        logger.error("prediction_failed")
        raise HTTPException(500, "Prediction failed") from None
    logger.info("prediction_completed")
    return validated
