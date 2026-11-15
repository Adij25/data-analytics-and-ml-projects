"""FastAPI service.   uvicorn app.main:app --port 8000

Model source (env MODEL_SOURCE):
  file   (default) -> joblib pipeline at MODEL_PATH (default models/churn_pipeline.joblib)
  mlflow           -> MLflow registry alias, MODEL_URI (default models:/churn-xgb@production)
"""
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException

from app.schemas import CustomerIn, HealthOut, PredictionOut, Reason
from src import config as C

STATE: dict = {"pipeline": None, "threshold": 0.5}


def _pretty(n: str) -> str:
    return n.replace("num__", "").replace("cat__", "").replace("_", " ")


def load_model():
    if os.getenv("MODEL_SOURCE", "file") == "mlflow":
        import mlflow.sklearn
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", C.MLFLOW_TRACKING_URI))
        pipe = mlflow.sklearn.load_model(os.getenv("MODEL_URI", f"models:/{C.REGISTERED_MODEL}@production"))
    else:
        pipe = joblib.load(os.getenv("MODEL_PATH", str(C.PIPELINE_PATH)))
    meta_path = Path(os.getenv("META_PATH", str(C.META_PATH)))
    thr = json.load(open(meta_path))["threshold"] if meta_path.exists() else 0.5
    return pipe, float(thr)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        STATE["pipeline"], STATE["threshold"] = load_model()
    except Exception as e:                      # /health will report model_loaded=False
        print("model load failed:", e)
    yield


app = FastAPI(title="Churn Prediction API", version="1.0", lifespan=lifespan)

@app.get("/")
def home():
    return {
        "message": "Customer Churn Prediction API",
        "status": "Running",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "prediction": "/predict",
            "documentation": "/docs"
        }
    }

def top_reasons(pipe, X: pd.DataFrame, k: int = 3):
    """Per-customer drivers from XGBoost's native SHAP values (pred_contribs); [] for other model types."""
    clf = pipe.named_steps["clf"]
    if not hasattr(clf, "get_booster"):
        return []
    import xgboost as xgb
    Xt = pipe[:-1].transform(X)
    contribs = clf.get_booster().predict(xgb.DMatrix(np.asarray(Xt)), pred_contribs=True)[0][:-1]  # drop bias
    names = [_pretty(n) for n in pipe.named_steps["prep"].get_feature_names_out()]
    order = np.argsort(-np.abs(contribs))[:k]
    return [Reason(feature=names[i], impact=round(float(contribs[i]), 4),
                   direction="increases churn risk" if contribs[i] > 0 else "decreases churn risk") for i in order]


@app.get("/health", response_model=HealthOut)
def health():
    ok = STATE["pipeline"] is not None
    return HealthOut(status="ok" if ok else "degraded", model_loaded=ok, threshold=STATE["threshold"] if ok else None)


@app.post("/predict", response_model=PredictionOut)
def predict(customer: CustomerIn):
    pipe = STATE["pipeline"]
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    X = pd.DataFrame([customer.model_dump()])
    proba = float(pipe.predict_proba(X)[0, 1])
    return PredictionOut(churn_probability=round(proba, 4), churn_label="Yes" if proba >= STATE["threshold"] else "No",
                         threshold=STATE["threshold"], top_reasons=top_reasons(pipe, X))
