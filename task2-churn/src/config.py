"""Single place for constants so train / evaluate / API all agree."""
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "task2_churn.csv"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
PIPELINE_PATH = MODELS_DIR / "churn_pipeline.joblib"
META_PATH = MODELS_DIR / "metadata.json"

TARGET = "Churn"
ID_COL = "customerID"

RAW_NUMERIC = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
RAW_CATEGORICAL = ["gender", "Partner", "Dependents", "PhoneService", "InternetService", "OnlineSecurity",
                   "TechSupport", "StreamingTV", "Contract", "PaperlessBilling", "PaymentMethod"]
ENGINEERED_NUMERIC = ["charges_per_tenure_month", "monthly_vs_avg", "has_support", "num_addons"]
ENGINEERED_CATEGORICAL = ["tenure_group"]

# ---- business economics (from the brief) ----
CONTACT_COST = 500          # cost of contacting one customer
SAVED_VALUE = 8000          # value of one saved customer
SAVE_RATE = 1.0             # P(contacted churner is saved). 1.0 = the brief taken literally; see sensitivity table
CAPACITY_FRAC = 0.40        # retention team can contact at most this share of customers (documented assumption)

MLFLOW_TRACKING_URI = f"sqlite:///{ROOT / 'mlflow.db'}"
MLFLOW_EXPERIMENT = "churn-prediction"
REGISTERED_MODEL = "churn-xgb"
