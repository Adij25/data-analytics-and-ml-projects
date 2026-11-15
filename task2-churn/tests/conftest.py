"""Trains a tiny model into a temp dir so the API tests are self-contained (no need to run train.py first)."""
import json
import joblib
import pytest
from xgboost import XGBClassifier

from src.preprocess import build_pipeline, load_and_clean


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    import os
    d = tmp_path_factory.mktemp("model")
    df = load_and_clean()
    pipe = build_pipeline(XGBClassifier(n_estimators=20, max_depth=3, eval_metric="logloss", random_state=42)).fit(
        df.drop(columns="Churn"), df["Churn"])
    joblib.dump(pipe, d / "pipe.joblib")
    json.dump({"threshold": 0.4}, open(d / "meta.json", "w"))
    os.environ.update(MODEL_SOURCE="file", MODEL_PATH=str(d / "pipe.joblib"), META_PATH=str(d / "meta.json"))
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
