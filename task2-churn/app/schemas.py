"""Pydantic models: input validation (allowed values, ranges) and response shape."""
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

YesNo = Literal["Yes", "No"]


class CustomerIn(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {
        "gender": "Female", "SeniorCitizen": 0, "Partner": "No", "Dependents": "No", "tenure": 3,
        "PhoneService": "Yes", "InternetService": "Fiber optic", "OnlineSecurity": "No", "TechSupport": "No",
        "StreamingTV": "Yes", "Contract": "Month-to-month", "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check", "MonthlyCharges": 89.5, "TotalCharges": 268.5}})

    gender: Literal["Female", "Male"]
    SeniorCitizen: Literal[0, 1]
    Partner: YesNo
    Dependents: YesNo
    tenure: int = Field(ge=0, le=120, description="months with the company")
    PhoneService: YesNo
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: YesNo
    TechSupport: YesNo
    StreamingTV: YesNo
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: YesNo
    PaymentMethod: Literal["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
    MonthlyCharges: Optional[float] = Field(default=None, ge=0, le=500)   # may be missing -> imputed by the pipeline
    TotalCharges: Optional[float] = Field(default=None, ge=0, le=100000)


class Reason(BaseModel):
    feature: str
    impact: float = Field(description="SHAP/contribution in log-odds; positive pushes towards churn")
    direction: Literal["increases churn risk", "decreases churn risk"]


class PredictionOut(BaseModel):
    churn_probability: float
    churn_label: Literal["Yes", "No"]
    threshold: float
    top_reasons: List[Reason]


class HealthOut(BaseModel):
    status: str
    model_loaded: bool
    threshold: Optional[float] = None
