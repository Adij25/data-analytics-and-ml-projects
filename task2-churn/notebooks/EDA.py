# %% [markdown]
# # Task 2 - Churn EDA
# Run from `task2-churn/`. EDA only uses descriptive statistics; no model is fitted here.

# %%
import sys
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
ROOT = Path.cwd() if (Path.cwd() / "src").exists() else Path.cwd().parent
sys.path.insert(0, str(ROOT))
from src.preprocess import load_and_clean, add_features
sns.set_theme(style="whitegrid")
(ROOT / "reports").mkdir(exist_ok=True)

raw = pd.read_csv(ROOT / "data/task2_churn.csv")
print(raw.shape); print(raw.dtypes.to_string())
print("blank TotalCharges:", (raw.TotalCharges.astype(str).str.strip() == "").sum(), "| missing MonthlyCharges:", raw.MonthlyCharges.isna().sum())
print("customerID unique:", raw.customerID.is_unique, "-> identifier only, dropped")

# %%
df = load_and_clean()
print("target balance:\n", df.Churn.value_counts(normalize=True).round(3))
print("remaining nulls after row-wise repair:", df.isna().sum()[df.isna().sum() > 0].to_dict())

# %%
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, col in zip(axes.ravel(), ["Contract", "InternetService", "PaymentMethod", "TechSupport", "OnlineSecurity", "SeniorCitizen"]):
    r = df.groupby(col).Churn.mean().sort_values(ascending=False) * 100
    sns.barplot(x=r.index.astype(str), y=r.values, ax=ax); ax.set_title(f"Churn % by {col}"); ax.set_xlabel("")
    ax.axhline(df.Churn.mean() * 100, ls="--", c="grey"); ax.tick_params(axis="x", rotation=15)
plt.tight_layout(); plt.savefig(ROOT / "reports/eda_churn_by_category.png", dpi=140); plt.show()

# %%
f = add_features(df)
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sns.boxplot(data=df, x="Churn", y="tenure", ax=axes[0]); sns.boxplot(data=df, x="Churn", y="MonthlyCharges", ax=axes[1])
r = f.groupby("tenure_group").Churn.mean().reindex(["0-12m", "13-24m", "25-48m", "49m+"]) * 100
sns.barplot(x=r.index, y=r.values, ax=axes[2]); axes[2].set_title("Churn % by tenure group")
plt.tight_layout(); plt.savefig(ROOT / "reports/eda_numeric.png", dpi=140); plt.show()
print(r.round(1).to_dict())
