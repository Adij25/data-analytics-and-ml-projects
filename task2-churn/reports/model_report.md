# Churn Prediction - Model Report

## 1. Problem
A telecom operator loses about 21.5% of its customers. The retention team can contact only a limited share of customers
(assumed 40%); each contact costs Rs 500 and a saved customer is worth Rs 8000.
Goal: rank customers by churn risk, explain why, and pick a contact threshold that maximises expected profit.

## 2. Approach
- Data: 7,000 customers. Fixed blank `TotalCharges` (text) and 150 missing `MonthlyCharges` using the same customer's other columns, dropped `customerID`.
- Stratified 70/15/15 split before any fitting; imputation, scaling and one-hot encoding live inside a scikit-learn `Pipeline` (fit on train only).
- 5 engineered features: charges per tenure month, monthly-vs-average charge, has-support flag, number of add-ons, tenure group.
- Models: Logistic Regression (baseline), Random Forest, XGBoost, each with class weights and with SMOTE (inside the pipeline). XGBoost tuned with Optuna (30+ trials, 5-fold stratified CV, objective PR-AUC).
- All runs tracked in MLflow; the best model is registered with alias `production` and served by FastAPI in Docker.

## 3. Results
Validation comparison (threshold 0.5):

| model         | imbalance    |   precision |   recall |     f1 |   roc_auc |   pr_auc |
|:--------------|:-------------|------------:|---------:|-------:|----------:|---------:|
| logreg        | class_weight |      0.4194 |   0.7478 | 0.5374 |    0.8081 |   0.5077 |
| logreg        | smote        |      0.42   |   0.7434 | 0.5367 |    0.8027 |   0.4973 |
| random_forest | class_weight |      0.4548 |   0.6239 | 0.5261 |    0.7935 |   0.4836 |
| random_forest | smote        |      0.4942 |   0.5619 | 0.5259 |    0.7933 |   0.4856 |
| xgboost       | class_weight |      0.4236 |   0.6991 | 0.5275 |    0.7946 |   0.4811 |
| xgboost       | smote        |      0.5069 |   0.4867 | 0.4966 |    0.7929 |   0.4786 |

Final tuned XGBoost on the **test set** (scored once, at threshold 0.31):

| Metric | Value |
|---|---|
| Precision | 0.444 |
| Recall | 0.761 |
| F1 | 0.561 |
| ROC-AUC | 0.822 |
| PR-AUC | 0.535 (baseline = churn rate 0.215) |
| Customers contacted | 37% |
| Expected profit on test (Rs) | 1,182,500 |

Figures: `pr_curve_test.png`, `calibration_test.png`, `confusion_matrix_test.png`, `optuna_history.png`, `optuna_param_importance.png`.

## 4. Threshold justification
Expected profit = TP x 1 x 8000 - (TP + FP) x 500. With the brief's numbers a contact pays off whenever
P(churn) > 500/8000 = 6.25%, which would mean contacting almost everyone. Because the team can only contact
40% of customers, the threshold is the profit-maximising one **within that capacity**, chosen on the validation set
(t = 0.31). Sensitivity to the probability that a contacted churner is actually saved:

|   save_rate |   best_t_unconstrained | contacted_unconstrained   |   best_t_within_capacity | contacted_within_capacity   |
|------------:|-----------------------:|:--------------------------|-------------------------:|:----------------------------|
|         1   |                   0.08 | 71%                       |                     0.31 | 38%                         |
|         0.5 |                   0.19 | 54%                       |                     0.31 | 38%                         |
|         0.3 |                   0.32 | 37%                       |                     0.32 | 37%                         |

If real save rates are lower than 100% (they usually are), the optimal threshold rises and fewer customers are contacted.

## 5. Top churn drivers (SHAP)
1. **Contract Month-to-month** (mean |SHAP| 0.78)
2. **tenure** (mean |SHAP| 0.45)
3. **MonthlyCharges** (mean |SHAP| 0.34)
4. **charges per tenure month** (mean |SHAP| 0.31)
5. **PaymentMethod Electronic check** (mean |SHAP| 0.18)

Plain-language reading of the data (from EDA): month-to-month customers churn at 34.7% vs 3.4% on two-year contracts; fibre
customers churn at 33.4% vs 13.7% for DSL; customers in their first year churn at 41.9% vs 2.4% after four years; electronic-check payers churn at 26.2%.
Churners also pay more (median Rs 84.8 vs 58.6 per month).

## 6. Business recommendations
1. **Move month-to-month customers onto 1-2 year contracts** with a discount or free add-on: contract type is the strongest single separator of churn.
2. **Onboarding programme for the first 12 months**: proactive check-ins and a first-year offer, since tenure under a year carries the highest risk.
3. **Review fibre pricing and quality**, and bundle security/tech-support add-ons (customers with support churn less, 19.2% vs 25.7%); target the high-risk list from the API, not the whole base.
