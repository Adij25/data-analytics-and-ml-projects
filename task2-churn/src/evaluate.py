"""Part 3 - evaluation helpers: metrics, expected-profit threshold selection, plots."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score, ConfusionMatrixDisplay)

from src import config as C


def metrics_at(y, proba, threshold=0.5) -> dict:
    pred = (proba >= threshold).astype(int)
    return {"precision": precision_score(y, pred, zero_division=0), "recall": recall_score(y, pred),
            "f1": f1_score(y, pred), "roc_auc": roc_auc_score(y, proba), "pr_auc": average_precision_score(y, proba)}


def profit_curve(y, proba, cost=C.CONTACT_COST, value=C.SAVED_VALUE, save_rate=C.SAVE_RATE, grid=None) -> pd.DataFrame:
    """Expected profit if we contact everyone with proba >= t:
         profit = TP * save_rate * value  -  (TP + FP) * cost
    TP = churners contacted, FP = non-churners contacted (cost wasted)."""
    y = np.asarray(y)
    grid = np.linspace(0.02, 0.95, 94) if grid is None else grid
    rows = []
    for t in grid:
        pred = proba >= t
        tp, fp = int((pred & (y == 1)).sum()), int((pred & (y == 0)).sum())
        rows.append({"threshold": t, "contacted": tp + fp, "contacted_frac": (tp + fp) / len(y), "tp": tp, "fp": fp,
                     "precision": tp / max(tp + fp, 1), "recall": tp / max((y == 1).sum(), 1),
                     "profit": tp * save_rate * value - (tp + fp) * cost})
    return pd.DataFrame(rows)


def best_threshold(y, proba, capacity_frac=C.CAPACITY_FRAC, **kw):
    """Threshold with maximum expected profit subject to contacting at most `capacity_frac` of customers."""
    pc = profit_curve(y, proba, **kw)
    unconstrained = pc.loc[pc.profit.idxmax()]
    ok = pc[pc.contacted_frac <= capacity_frac]
    constrained = ok.loc[ok.profit.idxmax()] if len(ok) else pc.loc[pc.contacted_frac.idxmin()]
    return unconstrained, constrained, pc


# ----------------------------- plots -----------------------------
def plot_pr_curve(y, proba, path, threshold=None):
    p, r, t = precision_recall_curve(y, proba)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.plot(r, p, lw=2, label=f"PR-AUC = {average_precision_score(y, proba):.3f}")
    ax.axhline(np.mean(y), ls="--", c="grey", label=f"baseline = {np.mean(y):.2f}")
    if threshold is not None:
        pred = proba >= threshold
        ax.scatter([recall_score(y, pred)], [precision_score(y, pred)], c="red", zorder=5, label=f"threshold {threshold:.2f}")
    ax.set(xlabel="Recall", ylabel="Precision", title="Precision-Recall curve"); ax.legend()
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_calibration(y, proba, path, n_bins=10):
    frac, mean = calibration_curve(y, proba, n_bins=n_bins, strategy="quantile")
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.plot([0, 1], [0, 1], "k--", label="perfect"); ax.plot(mean, frac, "o-", label="model")
    ax.set(xlabel="Mean predicted probability", ylabel="Observed churn rate", title="Calibration curve"); ax.legend()
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_confusion(y, proba, threshold, path):
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    ConfusionMatrixDisplay(confusion_matrix(y, proba >= threshold), display_labels=["Stay", "Churn"]).plot(ax=ax, colorbar=False)
    ax.set_title(f"Confusion matrix (threshold {threshold:.2f})")
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_profit(pc, chosen, path, capacity_frac=C.CAPACITY_FRAC):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(pc.threshold, pc.profit / 1e3, lw=2)
    ax.axvline(chosen["threshold"], c="red", ls="--", label=f"chosen t = {chosen['threshold']:.2f}")
    cap = pc[pc.contacted_frac <= capacity_frac]
    if len(cap): ax.axvspan(cap.threshold.min(), pc.threshold.max(), alpha=.08, label=f"within capacity (<= {capacity_frac:.0%} contacted)")
    ax.set(xlabel="Decision threshold", ylabel="Expected profit (Rs thousand)", title="Expected profit vs threshold (validation)"); ax.legend()
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
