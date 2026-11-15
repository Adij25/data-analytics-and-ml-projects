"""Bonus - Evidently data-drift report: training data vs a simulated drifted batch.   python -m src.drift"""
import numpy as np
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

from src import config as C
from src.preprocess import load_and_clean, split


def simulate_drift(X, seed=C.SEED):
    rng = np.random.default_rng(seed)
    d = X.sample(len(X), replace=True, random_state=seed).copy()
    d["tenure"] = (d["tenure"] * 0.6).round().astype(int)                       # newer customer base
    d["MonthlyCharges"] = d["MonthlyCharges"] * 1.25                             # price rise
    d["TotalCharges"] = d["MonthlyCharges"] * d["tenure"].clip(lower=1)
    flip = rng.random(len(d)) < 0.30
    d.loc[flip, "Contract"] = "Month-to-month"                                   # more flexible contracts
    return d


if __name__ == "__main__":
    X_tr, *_ = split(load_and_clean())
    drifted = simulate_drift(X_tr)
    rep = Report(metrics=[DataDriftPreset()])
    rep.run(reference_data=X_tr.reset_index(drop=True), current_data=drifted.reset_index(drop=True))
    C.REPORTS_DIR.mkdir(exist_ok=True)
    rep.save_html(str(C.REPORTS_DIR / "drift_report.html"))
    print("saved", C.REPORTS_DIR / "drift_report.html")
