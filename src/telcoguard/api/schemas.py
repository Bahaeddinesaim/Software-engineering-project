"""Strict request and response contracts matching training features."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Binary = Literal["Yes", "No"]
Service = Literal["Yes", "No", "No internet service"]


class Customer(BaseModel):
    """Accept all 19 predictors; explicit nulls are imputed by the fitted pipeline."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    gender: Literal["Female", "Male"] | None
    SeniorCitizen: int | None = Field(ge=0, le=1)
    Partner: Binary | None
    Dependents: Binary | None
    tenure: int | None = Field(ge=0, le=1200)
    PhoneService: Binary | None
    MultipleLines: Literal["Yes", "No", "No phone service"] | None
    InternetService: Literal["DSL", "Fiber optic", "No"] | None
    OnlineSecurity: Service | None
    OnlineBackup: Service | None
    DeviceProtection: Service | None
    TechSupport: Service | None
    StreamingTV: Service | None
    StreamingMovies: Service | None
    Contract: Literal["Month-to-month", "One year", "Two year"] | None
    PaperlessBilling: Binary | None
    PaymentMethod: (
        Literal[
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ]
        | None
    )
    MonthlyCharges: float | None = Field(ge=0, le=100000)
    TotalCharges: float | None = Field(ge=0, le=100000000)


class Prediction(BaseModel):
    """Describe estimated churn risk, without claiming probability calibration."""

    prediction: Literal[0, 1]
    churn_label: Binary
    churn_probability: float = Field(ge=0, le=1)
    risk_level: Literal["low", "medium", "high"]
    model_version: str
