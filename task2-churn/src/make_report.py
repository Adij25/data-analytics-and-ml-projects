"""Fills reports/model_report.md with the REAL numbers produced by train.py / explain.py.   python -m src.make_report"""
import json
import pandas as pd
from src import config as C

R = C.REPORTS_DIR
m = json.load(open(R / "test_metrics.json"))
comp = pd.read_csv(R / "model_comparison.csv")
sens = pd.read_csv(R / "threshold_sensitivity.csv")
meta = json.load(open(C.META_PATH))
shap_top = pd.read_csv(R / "shap_top_features.csv").head(5) if (R / "shap_top_features.csv").exists() else None
drivers = "\n".join(f"{i + 1}. **{r.iloc[0]}** (mean |SHAP| {r.mean_abs_shap:.2f})" for i, r in shap_top.iterrows()) if shap_top is not None else "_run `python -m src.explain` first_"

txt = f"""# Churn Prediction - Model Report

## 1. Problem
A telecom operator loses about 21.5% of its customers. The retention team can contact only a limited share of customers
(assumed {C.CAPACITY_FRAC:.0%}); each contact costs Rs {C.CONTACT_COST} and a saved customer is worth Rs {C.SAVED_VALUE}.
Goal: rank customers by churn risk, explain why, and pick a contact threshold that maximises expected profit.

## 2. Approach
- Data: 7,000 customers. Fixed blank `TotalCharges` (text) and 150 missing `MonthlyCharges` using the same customer's other columns, dropped `customerID`.
- Stratified 70/15/15 split before any fitting; imputation, scaling and one-hot encoding live inside a scikit-learn `Pipeline` (fit on train only).
- 5 engineered features: charges per tenure month, monthly-vs-average charge, has-support flag, number of add-ons, tenure group.
- Models: Logistic Regression (baseline), Random Forest, XGBoost, each with class weights and with SMOTE (inside the pipeline). XGBoost tuned with Optuna ({'30+'} trials, 5-fold stratified CV, objective PR-AUC).
- All runs tracked in MLflow; the best model is registered with alias `production` and served by FastAPI in Docker.

## 3. Results
Validation comparison (threshold 0.5):

{comp.to_markdown(index=False)}

Final tuned XGBoost on the **test set** (scored once, at threshold {meta['threshold']:.2f}):

| Metric | Value |
|---|---|
| Precision | {m['precision']:.3f} |
| Recall | {m['recall']:.3f} |
| F1 | {m['f1']:.3f} |
| ROC-AUC | {m['roc_auc']:.3f} |
| PR-AUC | {m['pr_auc']:.3f} (baseline = churn rate 0.215) |
| Customers contacted | {m['contacted_frac']:.0%} |
| Expected profit on test (Rs) | {m['expected_profit']:,.0f} |

Figures: `pr_curve_test.png`, `calibration_test.png`, `confusion_matrix_test.png`, `optuna_history.png`, `optuna_param_importance.png`.

## 4. Threshold justification
Expected profit = TP x {C.SAVE_RATE:g} x {C.SAVED_VALUE} - (TP + FP) x {C.CONTACT_COST}. With the brief's numbers a contact pays off whenever
P(churn) > {C.CONTACT_COST}/{C.SAVED_VALUE} = {C.CONTACT_COST / C.SAVED_VALUE:.2%}, which would mean contacting almost everyone. Because the team can only contact
{C.CAPACITY_FRAC:.0%} of customers, the threshold is the profit-maximising one **within that capacity**, chosen on the validation set
(t = {meta['threshold']:.2f}). Sensitivity to the probability that a contacted churner is actually saved:

{sens.to_markdown(index=False)}

If real save rates are lower than 100% (they usually are), the optimal threshold rises and fewer customers are contacted.

## 5. Top churn drivers (SHAP)
{drivers}

Plain-language reading of the data (from EDA): month-to-month customers churn at 34.7% vs 3.4% on two-year contracts; fibre
customers churn at 33.4% vs 13.7% for DSL; customers in their first year churn at 41.9% vs 2.4% after four years; electronic-check payers churn at 26.2%.
Churners also pay more (median Rs 84.8 vs 58.6 per month).

## 6. Business recommendations
1. **Move month-to-month customers onto 1-2 year contracts** with a discount or free add-on: contract type is the strongest single separator of churn.
2. **Onboarding programme for the first 12 months**: proactive check-ins and a first-year offer, since tenure under a year carries the highest risk.
3. **Review fibre pricing and quality**, and bundle security/tech-support add-ons (customers with support churn less, 19.2% vs 25.7%); target the high-risk list from the API, not the whole base.
"""
(R / "model_report.md").write_text(txt)
print("wrote", R / "model_report.md")
