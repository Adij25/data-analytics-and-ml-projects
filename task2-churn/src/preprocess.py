"""Part 1 - data preparation. Everything fitted (imputer/scaler/encoder) lives inside a Pipeline so it is
fit on training data only: no leakage."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src import config as C


def load_and_clean(path=C.DATA_PATH) -> pd.DataFrame:
    """Type fixes only (no statistics are learned here, so this is safe before the split)."""
    df = pd.read_csv(path)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip().replace("", np.nan), errors="coerce")
    df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
    # Row-wise repairs (use only the same customer's other columns, so no leakage): the blank TotalCharges rows
    # have tenure > 0, so estimate them as MonthlyCharges*tenure; a missing MonthlyCharges as TotalCharges/tenure.
    # Anything still missing (both absent) is median-imputed inside the pipeline, fit on train only.
    ten = df["tenure"].clip(lower=1)
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * ten)
    df["MonthlyCharges"] = df["MonthlyCharges"].fillna(df["TotalCharges"] / ten)
    df["SeniorCitizen"] = df["SeniorCitizen"].astype(int)
    df[C.TARGET] = df[C.TARGET].map({"Yes": 1, "No": 0}).astype(int)
    return df.drop(columns=[C.ID_COL])  # customerID has no predictive value


def split(df: pd.DataFrame, seed=C.SEED):
    """Stratified 70/15/15 split performed BEFORE any fitting."""
    X, y = df.drop(columns=[C.TARGET]), df[C.TARGET]
    X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=seed)
    X_va, X_te, y_va, y_te = train_test_split(X_tmp, y_tmp, test_size=0.50, stratify=y_tmp, random_state=seed)
    return X_tr, X_va, X_te, y_tr, y_va, y_te


def add_features(X: pd.DataFrame) -> pd.DataFrame:
    """Row-wise feature engineering (no fitted state). NaN-safe: missing charges stay NaN and are imputed later."""
    X = X.copy()
    tenure = X["tenure"].clip(lower=1)
    X["charges_per_tenure_month"] = X["TotalCharges"] / tenure                   # realised average monthly spend
    X["monthly_vs_avg"] = X["MonthlyCharges"] - X["charges_per_tenure_month"]    # >0: price rose vs history
    X["has_support"] = ((X["OnlineSecurity"] == "Yes") | (X["TechSupport"] == "Yes")).astype(int)
    X["num_addons"] = (X[["OnlineSecurity", "TechSupport", "StreamingTV"]] == "Yes").sum(axis=1)
    X["tenure_group"] = pd.cut(X["tenure"], bins=[-1, 12, 24, 48, np.inf],
                               labels=["0-12m", "13-24m", "25-48m", "49m+"]).astype(str)
    return X


def build_preprocessor() -> ColumnTransformer:
    num = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    cat = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer([
        ("num", num, C.RAW_NUMERIC + C.ENGINEERED_NUMERIC),
        ("cat", cat, C.RAW_CATEGORICAL + C.ENGINEERED_CATEGORICAL),
    ])


def build_pipeline(model, sampler=None):
    """features -> preprocess -> [SMOTE] -> model.  With a sampler an imblearn Pipeline is used so SMOTE only
    ever touches the training folds (it is skipped automatically at predict time)."""
    steps = [("features", FunctionTransformer(add_features)), ("prep", build_preprocessor())]
    if sampler is not None:
        from imblearn.pipeline import Pipeline as ImbPipeline
        return ImbPipeline(steps + [("smote", sampler), ("clf", model)])
    return Pipeline(steps + [("clf", model)])
