"""Part 4 - SHAP explainability.   python -m src.explain
Explains the saved pipeline on the VALIDATION split (the test set is kept for the single final evaluation)."""
import json
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from src import config as C
from src.preprocess import load_and_clean, split


def pretty(n: str) -> str:
    return n.replace("num__", "").replace("cat__", "").replace("_", " ")


def main():
    pipe = joblib.load(C.PIPELINE_PATH)
    _, X_va, _, _, y_va, _ = split(load_and_clean())
    Xt = pipe[:-1].transform(X_va)
    names = [pretty(n) for n in pipe.named_steps["prep"].get_feature_names_out()]
    Xt = pd.DataFrame(Xt, columns=names)
    explainer = shap.TreeExplainer(pipe.named_steps["clf"])
    sv = explainer(Xt)                                            # log-odds contributions

    plt.figure(); shap.summary_plot(sv, Xt, show=False, max_display=15)
    plt.tight_layout(); plt.savefig(C.REPORTS_DIR / "shap_summary.png", dpi=150, bbox_inches="tight"); plt.close()
    plt.figure(); shap.summary_plot(sv, Xt, plot_type="bar", show=False, max_display=15)
    plt.tight_layout(); plt.savefig(C.REPORTS_DIR / "shap_bar.png", dpi=150, bbox_inches="tight"); plt.close()

    imp = pd.Series(np.abs(sv.values).mean(0), index=names).sort_values(ascending=False)
    imp.head(10).to_csv(C.REPORTS_DIR / "shap_top_features.csv", header=["mean_abs_shap"])
    print("Top 10 drivers by mean |SHAP|:\n", imp.head(10).round(3))

    # two individual explanations: the most confidently predicted churner and non-churner (correctly classified)
    proba = pipe.predict_proba(X_va)[:, 1]
    thr = json.load(open(C.META_PATH))["threshold"]
    churn_idx = int(np.argmax(np.where(y_va.values == 1, proba, -1)))
    stay_idx = int(np.argmin(np.where(y_va.values == 0, proba, 2)))
    for tag, i in [("churner", churn_idx), ("non_churner", stay_idx)]:
        shap.plots.waterfall(sv[i], max_display=12, show=False)
        plt.title(f"{tag}: P(churn) = {proba[i]:.2f} (threshold {thr:.2f})")
        plt.savefig(C.REPORTS_DIR / f"shap_waterfall_{tag}.png", dpi=150, bbox_inches="tight"); plt.close()
        print(tag, "-> row", i, "P(churn)=%.2f" % proba[i], "| true label:", int(y_va.values[i]))


if __name__ == "__main__":
    main()
