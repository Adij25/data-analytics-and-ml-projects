"""Parts 2, 3, 5 - modelling, tuning, final evaluation and MLflow tracking.

    python -m src.train                 # full run (40 Optuna trials)
    python -m src.train --trials 30
    python -m src.train --quick         # 3 trials, for CI / smoke tests

Protocol (no leakage):
  * 70/15/15 stratified split first.
  * Model comparison + threshold choice use TRAIN (fit) and VALIDATION (score) only.
  * Optuna uses 5-fold stratified CV inside the TRAIN set only.
  * The TEST set is scored exactly once, at the very end, with the already-chosen threshold.
"""
import argparse
import json
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import optuna
import pandas as pd
from imblearn.over_sampling import SMOTE
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

from src import config as C
from src.evaluate import (best_threshold, metrics_at, plot_calibration, plot_confusion, plot_pr_curve, plot_profit)
from src.preprocess import build_pipeline, load_and_clean, split

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)


# ------------------------------------------------------------------ models
def make_model(name: str, spw: float, balanced: bool):
    """balanced=True -> class weights; balanced=False -> plain model (used together with SMOTE)."""
    if name == "logreg":
        return LogisticRegression(max_iter=2000, class_weight="balanced" if balanced else None, random_state=C.SEED)
    if name == "random_forest":
        return RandomForestClassifier(n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=C.SEED,
                                      class_weight="balanced_subsample" if balanced else None)
    if name == "xgboost":
        return XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                             scale_pos_weight=spw if balanced else 1.0, eval_metric="logloss",
                             tree_method="hist", n_jobs=-1, random_state=C.SEED)
    raise ValueError(name)


def log_run(run_name, params, metrics, artifacts=(), model=None, X_example=None, nested=False, tags=None):
    """One MLflow run = params + metrics + plot files (+ model artifact)."""
    with mlflow.start_run(run_name=run_name, nested=nested) as run:
        mlflow.log_params({k: (round(v, 6) if isinstance(v, float) else v) for k, v in params.items()})
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()})
        if tags: mlflow.set_tags(tags)
        for a in artifacts: mlflow.log_artifact(str(a))
        if model is not None:
            sig = infer_signature(X_example, model.predict_proba(X_example)[:, 1])
            mlflow.sklearn.log_model(model, artifact_path="model", signature=sig, input_example=X_example.head(3))
        return run.info.run_id


# ------------------------------------------------------------------ main
def main(n_trials: int, quick: bool):
    C.MODELS_DIR.mkdir(exist_ok=True); C.REPORTS_DIR.mkdir(exist_ok=True)
    mlflow.set_tracking_uri(C.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(C.MLFLOW_EXPERIMENT)
    np.random.seed(C.SEED)

    df = load_and_clean()
    X_tr, X_va, X_te, y_tr, y_va, y_te = split(df)
    spw = float((y_tr == 0).sum() / (y_tr == 1).sum())            # negatives / positives, from TRAIN only
    print(f"train={len(X_tr)} val={len(X_va)} test={len(X_te)} | churn rate {y_tr.mean():.3f} | scale_pos_weight={spw:.2f}")

    # ---------- Part 2a: 3 models x 2 imbalance strategies, scored on VALIDATION ----------
    rows = []
    for name in ["logreg", "random_forest", "xgboost"]:
        for strategy in ["class_weight", "smote"]:
            model = make_model(name, spw, balanced=(strategy == "class_weight"))
            sampler = SMOTE(random_state=C.SEED) if strategy == "smote" else None
            pipe = build_pipeline(model, sampler).fit(X_tr, y_tr)
            m = metrics_at(y_va, pipe.predict_proba(X_va)[:, 1], 0.5)
            rows.append({"model": name, "imbalance": strategy, **m})
            log_run(f"{name}__{strategy}", {"model": name, "imbalance": strategy, "stage": "comparison"},
                    {f"val_{k}": v for k, v in m.items()}, model=pipe, X_example=X_va, tags={"stage": "comparison"})
            print(f"{name:14s} {strategy:12s} PR-AUC={m['pr_auc']:.3f} ROC={m['roc_auc']:.3f} F1={m['f1']:.3f} recall={m['recall']:.3f}")
    comp = pd.DataFrame(rows).round(4)
    comp.to_csv(C.REPORTS_DIR / "model_comparison.csv", index=False)
    (C.REPORTS_DIR / "model_comparison.md").write_text(comp.to_markdown(index=False))
    print("\n", comp.to_string(index=False))

    # ---------- Part 2b: Optuna on XGBoost (5-fold stratified CV, train only, maximise PR-AUC) ----------
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=C.SEED)

    def params_from(trial):
        return dict(
            n_estimators=trial.suggest_int("n_estimators", 100, 600, step=50),
            max_depth=trial.suggest_int("max_depth", 2, 7),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            subsample=trial.suggest_float("subsample", 0.6, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            min_child_weight=trial.suggest_int("min_child_weight", 1, 10),
            reg_lambda=trial.suggest_float("reg_lambda", 1e-2, 20.0, log=True),
            reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 5.0, log=True),
            gamma=trial.suggest_float("gamma", 0.0, 3.0),
            scale_pos_weight=trial.suggest_float("scale_pos_weight", 1.0, spw * 1.5),
        )

    def objective(trial):
        p = params_from(trial)
        model = XGBClassifier(**p, eval_metric="logloss", tree_method="hist", n_jobs=1, random_state=C.SEED)
        # whole pipeline inside CV -> imputer/scaler/encoder are re-fit on each training fold only
        return cross_val_score(build_pipeline(model), X_tr, y_tr, cv=cv, scoring="average_precision", n_jobs=-1).mean()

    def trial_logger(study, trial):  # one nested MLflow run per trial
        with mlflow.start_run(run_name=f"optuna_trial_{trial.number}", nested=True):
            mlflow.log_params(trial.params); mlflow.log_metric("cv_pr_auc", trial.value)

    with mlflow.start_run(run_name="xgboost_optuna_tuning") as parent:
        study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=C.SEED))
        study.optimize(objective, n_trials=n_trials, callbacks=[trial_logger])
        print(f"\nbest CV PR-AUC={study.best_value:.4f}\nbest params={study.best_params}")

        from optuna.visualization.matplotlib import plot_optimization_history, plot_param_importances
        ax = plot_optimization_history(study); ax.figure.set_size_inches(7, 4.5); ax.figure.tight_layout()
        ax.figure.savefig(C.REPORTS_DIR / "optuna_history.png", dpi=150); plt.close("all")
        ax = plot_param_importances(study); ax.figure.set_size_inches(7, 5); ax.figure.tight_layout()
        ax.figure.savefig(C.REPORTS_DIR / "optuna_param_importance.png", dpi=150); plt.close("all")
        mlflow.log_params({f"best_{k}": v for k, v in study.best_params.items()})
        mlflow.log_metric("best_cv_pr_auc", study.best_value)
        mlflow.log_artifact(str(C.REPORTS_DIR / "optuna_history.png"))
        mlflow.log_artifact(str(C.REPORTS_DIR / "optuna_param_importance.png"))

    # ---------- final model: tuned XGBoost fit on TRAIN ----------
    best = XGBClassifier(**study.best_params, eval_metric="logloss", tree_method="hist", n_jobs=-1, random_state=C.SEED)
    final = build_pipeline(best).fit(X_tr, y_tr)
    p_va = final.predict_proba(X_va)[:, 1]

    # ---------- Part 3: threshold chosen on VALIDATION using the profit model ----------
    unc, cap, pc = best_threshold(y_va, p_va)                        # cap = best profit within retention capacity
    thr = float(cap["threshold"])
    pc.to_csv(C.REPORTS_DIR / "profit_curve_validation.csv", index=False)
    plot_profit(pc, cap, C.REPORTS_DIR / "profit_vs_threshold.png")
    sens = []
    for sr in [1.0, 0.5, 0.3]:                                        # sensitivity to the "customer is saved" probability
        u, c, _ = best_threshold(y_va, p_va, save_rate=sr)
        sens.append({"save_rate": sr, "best_t_unconstrained": round(u.threshold, 2), "contacted_unconstrained": f"{u.contacted_frac:.0%}",
                     "best_t_within_capacity": round(c.threshold, 2), "contacted_within_capacity": f"{c.contacted_frac:.0%}"})
    pd.DataFrame(sens).to_csv(C.REPORTS_DIR / "threshold_sensitivity.csv", index=False)
    print(f"\nthreshold (max profit, <= {C.CAPACITY_FRAC:.0%} contacted) = {thr:.2f}; "
          f"unconstrained optimum would be {unc['threshold']:.2f} ({unc['contacted_frac']:.0%} contacted)")

    # ---------- the ONE test-set evaluation ----------
    p_te = final.predict_proba(X_te)[:, 1]
    test_m = metrics_at(y_te, p_te, thr)
    pred = p_te >= thr
    tp, fp = int((pred & (y_te == 1)).sum()), int((pred & (y_te == 0)).sum())
    test_m["expected_profit"] = tp * C.SAVE_RATE * C.SAVED_VALUE - (tp + fp) * C.CONTACT_COST
    test_m["contacted_frac"] = float(pred.mean())
    print("TEST:", {k: round(v, 4) for k, v in test_m.items()})
    plot_pr_curve(y_te, p_te, C.REPORTS_DIR / "pr_curve_test.png", thr)
    plot_calibration(y_te, p_te, C.REPORTS_DIR / "calibration_test.png")
    plot_confusion(y_te, p_te, thr, C.REPORTS_DIR / "confusion_matrix_test.png")
    json.dump({k: float(v) for k, v in test_m.items()}, open(C.REPORTS_DIR / "test_metrics.json", "w"), indent=2)

    # ---------- save artefacts + MLflow registry ----------
    joblib.dump(final, C.PIPELINE_PATH)
    meta = {"threshold": thr, "model": "xgboost", "best_params": study.best_params, "test_metrics": test_m,
            "cost": C.CONTACT_COST, "value": C.SAVED_VALUE, "save_rate": C.SAVE_RATE, "capacity_frac": C.CAPACITY_FRAC,
            "feature_names": list(final.named_steps["prep"].get_feature_names_out())}
    json.dump(meta, open(C.META_PATH, "w"), indent=2, default=float)

    plots = [C.REPORTS_DIR / f for f in ["pr_curve_test.png", "calibration_test.png", "confusion_matrix_test.png",
                                         "profit_vs_threshold.png", "optuna_history.png", "optuna_param_importance.png"]]
    run_id = log_run("xgboost_final", {"model": "xgboost", "imbalance": "scale_pos_weight (tuned)", "threshold": thr,
                                       **study.best_params},
                     {**{f"test_{k}": v for k, v in test_m.items()}, "val_pr_auc": metrics_at(y_va, p_va, thr)["pr_auc"]},
                     artifacts=plots + [C.REPORTS_DIR / "model_comparison.csv", C.META_PATH],
                     model=final, X_example=X_va, tags={"stage": "final"})

    client = MlflowClient()
    mv = mlflow.register_model(f"runs:/{run_id}/model", C.REGISTERED_MODEL)
    client.set_registered_model_alias(C.REGISTERED_MODEL, "production", mv.version)   # stages are deprecated; use aliases
    print(f"registered {C.REGISTERED_MODEL} v{mv.version} -> alias 'production'  (run {run_id})")
    print("Browse runs:  mlflow ui --backend-store-uri", C.MLFLOW_TRACKING_URI)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--quick", action="store_true", help="3 trials; for smoke tests")
    a = ap.parse_args()
    main(3 if a.quick else max(a.trials, 30), a.quick)
