# Customer Churn Prediction Dashboard – End-to-End MLOps

An end-to-end **Customer Churn Prediction** project that uses machine learning to identify customers who are likely to leave a service. The project combines data preprocessing, exploratory data analysis, model training and optimization, model evaluation, explainable AI, drift monitoring, and a REST API.

A **React-based interactive dashboard** provides a user-friendly interface to check model status, enter customer details, generate churn predictions, understand prediction results, and view the data drift report.

---

## 1. Project Overview

Customer churn is an important business problem because retaining existing customers is often more cost-effective than acquiring new ones.

The objective of this project is to build a machine learning solution that predicts whether a customer is likely to churn based on customer information, service subscriptions, contract details, and billing information.

The project follows an end-to-end machine learning workflow:

1. Load and explore the customer churn dataset.
2. Clean and preprocess the data.
3. Split the data into training, validation, and testing sets.
4. Build and compare machine learning models.
5. Optimize model hyperparameters using Optuna.
6. Evaluate model performance and select a business-oriented prediction threshold.
7. Explain model predictions using SHAP.
8. Track experiments and register the trained model using MLflow.
9. Monitor data drift using Evidently.
10. Expose predictions through a FastAPI backend.
11. Provide an interactive React dashboard for users.

## 2. Technology Stack

| Component | Technologies |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Data Visualization | Matplotlib |
| Machine Learning | Scikit-learn, XGBoost |
| Imbalanced Data Handling | imbalanced-learn, SMOTE |
| Hyperparameter Optimization | Optuna |
| Model Explainability | SHAP |
| Experiment Tracking | MLflow |
| Data Drift Monitoring | Evidently |
| Backend | FastAPI |
| API Validation | Pydantic |
| Frontend | React, Vite, JavaScript |
| Dashboard Charts | Recharts |
| Icons | Lucide React |
| Model Persistence | Joblib |
| Testing | Pytest |
| Containerization | Docker |
| CI/CD | GitHub Actions |

## 3. Project Structure

```text
task2-churn/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and prediction endpoints
│   └── schemas.py              # Pydantic request and response validation
│
├── data/
│   └── task2_churn.csv         # Original customer churn dataset
│
├── frontend/
│   ├── public/
│   │   └── reports/
│   │       └── drift_report.html
│   ├── src/
│   │   ├── App.jsx             # Main React dashboard
│   │   ├── App.css             # Dashboard styling
│   │   ├── index.css           # Global styles
│   │   └── main.jsx            # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js          # Development server and API proxy
│
├── models/
│   ├── churn_pipeline.joblib   # Trained machine learning pipeline
│   └── metadata.json           # Model metadata and decision threshold
│
├── notebooks/
│   ├── EDA.ipynb               # Exploratory data analysis notebook
│   └── EDA.py
│
├── reports/
│   ├── calibration_test.png
│   ├── confusion_matrix_test.png
│   ├── drift_report.html
│   ├── eda_churn_by_category.png
│   ├── eda_numeric.png
│   ├── model_comparison.csv
│   ├── model_comparison.md
│   ├── model_report.md
│   ├── optuna_history.png
│   ├── optuna_param_importance.png
│   ├── pr_curve_test.png
│   ├── shap_bar.png
│   ├── shap_summary.png
│   ├── shap_top_features.csv
│   ├── shap_waterfall_churner.png
│   ├── shap_waterfall_non_churner.png
│   ├── test_metrics.json
│   └── threshold_sensitivity.csv
│
├── src/
│   ├── config.py               # Project configuration
│   ├── preprocess.py           # Data preprocessing and feature engineering
│   ├── train.py                # Model training and Optuna optimization
│   ├── evaluate.py              # Model evaluation and threshold analysis
│   ├── explain.py               # SHAP model explanations
│   ├── drift.py                 # Data drift monitoring
│   └── make_report.py           # Automated model report generation
│
├── tests/
│   ├── conftest.py
│   └── test_api.py              # API and validation tests
│
├── Dockerfile
├── requirements.txt
├── requirements-api.txt
└── .github/
    └── workflows/
        └── ci.yml               # GitHub Actions CI workflow
```

*Note: Generated MLflow tracking files and other local development artifacts may also be present in the project directory.*

## 4. Machine Learning Workflow

### 4.1 Exploratory Data Analysis

Exploratory Data Analysis is performed using the dataset in `data/task2_churn.csv`.

The analysis helps understand:
- Customer demographics and service subscriptions.
- Customer tenure and billing information.
- Distribution of churn and non-churn customers.
- Relationships between customer attributes and churn.
- Patterns that can help identify potential churn indicators.

EDA visualizations are generated and stored in the `reports/` directory.

### 4.2 Data Preprocessing

The preprocessing workflow is implemented in `src/preprocess.py`.

It includes:
- Data cleaning and preparation.
- Handling missing values using imputers.
- Numerical feature scaling.
- Categorical feature encoding.
- Feature engineering.
- Training, validation, and test data splitting.
- Construction of a reusable Scikit-learn preprocessing pipeline.

SMOTE is integrated into an imbalanced-learn pipeline to handle class imbalance during training.

### 4.3 Model Training and Optimization

Model training and experimentation are implemented in `src/train.py`.

The workflow includes:
- Comparing multiple machine learning models.
- Hyperparameter optimization using Optuna.
- Cross-validation.
- Final model evaluation.
- MLflow experiment tracking.
- Model registration.

The full training workflow runs 40 Optuna trials by default. A quick mode is also available for a smaller smoke test.

### 4.4 Model Evaluation

The evaluation workflow is implemented in `src/evaluate.py`.

The project generates evaluation outputs such as:
- Confusion matrix.
- Precision-recall curve.
- Calibration plot.
- Model comparison results.
- Threshold sensitivity analysis.
- Test-set metrics.

The generated reports and plots are stored in `reports/`.

### 4.5 Model Explainability with SHAP

SHAP is used to understand how individual features influence model predictions.

The explainability workflow is implemented in `src/explain.py`.

Generated outputs include:
- SHAP summary plot.
- SHAP feature importance plot.
- Top feature contribution report.
- Individual customer prediction explanations.

The FastAPI prediction response also includes up to three important prediction drivers when the loaded model supports the native XGBoost contribution interface.

### 4.6 Data Drift Monitoring

The project includes data drift monitoring using Evidently.

The implementation is available in `src/drift.py`.

It generates an interactive HTML report:

```text
reports/drift_report.html
```

This report can be opened independently or viewed inside the React dashboard.

### 4.7 MLflow Experiment Tracking

MLflow is used to track model experiments, compare training runs, and manage the registered model.

The experiment name is:

```text
churn-prediction
```

The registered model name is:

```text
churn-xgb
```

The production model alias is:

```text
production
```

## 5. React Dashboard

The frontend is developed using React and Vite. It communicates with the FastAPI backend to display model information and generate customer churn predictions.

### Dashboard Features

**1. Overview**
- Displays API and model loading status.
- Shows the active prediction threshold.
- Provides a summary of the latest prediction.

**2. Predict Churn**
- Provides an interactive customer input form.
- Accepts customer demographic, service, contract, and billing information.
- Sends customer details to the FastAPI prediction endpoint.
- Displays the predicted churn probability.
- Displays the predicted churn label.
- Shows the decision threshold and top prediction reasons.

**3. Data Drift Report**
- Embeds the generated Evidently HTML report.
- Allows the report to be opened separately in a browser.

**4. Model Insights**
- Displays the latest prediction's important SHAP-based reasons.
- Shows whether individual features increase or decrease churn risk.

### Frontend Technologies

- React – component-based user interface.
- Vite – frontend development and build tooling.
- JavaScript – dashboard functionality and API integration.
- Recharts – chart visualizations.
- Lucide React – dashboard icons.
- CSS – responsive layout and styling.

### Frontend and Backend Communication

The React frontend communicates with the FastAPI backend using HTTP requests.

During local development, Vite proxies the API requests to:

```text
http://127.0.0.1:8000
```

The frontend uses the following backend endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Check API and model status |
| POST | `/predict` | Generate customer churn prediction |

The React dashboard runs separately on port `5173`.

## 6. Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.10 or a compatible version supported by the project dependencies.
- Node.js and npm.
- Git (optional, for cloning the repository).

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd task2-churn
```

Alternatively, download and extract the project ZIP file.

### Step 2: Create a Python Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

## 7. Train the Machine Learning Model

Run the following commands from the project root directory.

### Full Training

```bash
python -m src.train
```

This runs the complete training workflow with 40 Optuna trials. The full run may take approximately 10–20 minutes, depending on the system.

### Quick Training

```bash
python -m src.train --quick
```

This runs a smaller smoke test with 3 Optuna trials.

### Generate SHAP Explanations

```bash
python -m src.explain
```

### Generate the Model Report

```bash
python -m src.make_report
```

The generated report is saved to:

```text
reports/model_report.md
```

### Generate the Data Drift Report

```bash
python -m src.drift
```

The generated HTML report is saved to:

```text
reports/drift_report.html
```

**Important:** Train the model before starting the API if the model artifacts are not already available.

## 8. Run MLflow

Start the MLflow UI:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Open the following address:

```text
http://localhost:5000
```

To compare model experiments:

1. Open the `churn-prediction` experiment.
2. Select the required experiment runs.
3. Click **Compare**.
4. Review the model performance and hyperparameter results.

To inspect the registered model:

1. Open the Models section.
2. Select `churn-xgb`.
3. Verify the registered model and its `production` alias.

## 9. Run the FastAPI Backend

Start the backend from the project root directory:

```bash
uvicorn app.main:app --port 8000 --reload
```

The API loads the trained pipeline from:

```text
models/churn_pipeline.joblib
```

### API Documentation

Open the interactive Swagger documentation:

```text
http://localhost:8000/docs
```

### Check API Health

```bash
curl http://localhost:8000/health
```

The health endpoint reports whether the model loaded successfully and returns the configured prediction threshold.

### Generate a Customer Churn Prediction

Send a POST request to:

```text
http://localhost:8000/predict
```

Example request:

```bash
curl -X POST http://localhost:8000/predict \
-H "Content-Type: application/json" \
-d '{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "No",
  "Dependents": "No",
  "tenure": 3,
  "PhoneService": "Yes",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "TechSupport": "No",
  "StreamingTV": "Yes",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 89.5,
  "TotalCharges": 268.5
}'
```

The API returns:
- Churn probability.
- Predicted churn label (`Yes` or `No`).
- Decision threshold.
- Important prediction reasons, when supported by the model.

The request is validated using Pydantic schemas defined in `app/schemas.py`.

## 10. Run the React Frontend

Open a second terminal while keeping the FastAPI backend running.

Navigate to the frontend directory:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open the dashboard in your browser:

```text
http://localhost:5173
```

### Running the Complete Application

Both services must be running for the dashboard to communicate with the prediction API.

| Application | Local URL |
|---|---|
| React Dashboard | http://localhost:5173 |
| FastAPI Backend | http://localhost:8000 |
| Swagger API Documentation | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |

## 11. Run the Automated Tests

The project includes Pytest-based tests for the API and validation behavior.

Run:

```bash
pytest -q
```

The test suite contains 9 tests.

## 12. Docker Deployment

The Docker image copies the trained model artifacts, so train the model before building the image.

### Build the Docker Image

```bash
docker build -t churn-api .
```

### Run the Container

```bash
docker run -p 8000:8000 churn-api
```

The API will be available at:

```text
http://localhost:8000
```

### Dependency Version Compatibility

The trained model is serialized using Joblib. The versions of Scikit-learn, XGBoost, Pandas, and NumPy used during training should be compatible with the versions installed in the Docker image.

A version mismatch can cause model-loading or unpickling errors.

Check the installed package versions:

```bash
pip freeze
```

Ensure the relevant package versions are pinned consistently in `requirements.txt` and `requirements-api.txt`.

## 13. Important Design Decisions

### Preventing Data Leakage

The project follows a leakage-aware machine learning workflow:

- Data is split before preprocessing.
- Imputation, scaling, and categorical encoding are included in the preprocessing pipeline.
- SMOTE is applied within the imbalanced-learn pipeline so that it operates only on training data during cross-validation.
- Optuna cross-validation evaluates the complete pipeline separately for each fold.
- The decision threshold is selected using validation data.
- The test set is evaluated only once for final performance reporting.

These practices help ensure that the evaluation process reflects performance on unseen data.

### Business-Oriented Decision Threshold

Instead of automatically using a default threshold of 0.5, the project selects a threshold based on an expected-profit calculation.

The expected-profit formula is:

```text
Expected Profit =
(TP × SAVE_RATE × 8000) - ((TP + FP) × 500)
```

Where:

- `TP` = True Positives.
- `FP` = False Positives.
- `SAVE_RATE` = Assumed success rate of customer retention.
- `8000` = Assumed business value for a successfully retained customer.
- `500` = Assumed cost per retention attempt.

The threshold is optimized subject to the retention capacity configured through `CAPACITY_FRAC` in `src/config.py`.

**Business assumption:** `CAPACITY_FRAC` and `SAVE_RATE` are configurable assumptions, not universal business constants. They should be adjusted to match the actual organization's retention capacity and campaign success rate.

## 14. Generated Artifacts

The project generates several artifacts for evaluation, explainability, monitoring, and deployment.

| Artifact | Description |
|---|---|
| `models/churn_pipeline.joblib` | Trained machine learning pipeline |
| `models/metadata.json` | Model metadata and prediction threshold |
| `reports/model_report.md` | Generated model evaluation report |
| `reports/model_comparison.csv` | Model comparison results |
| `reports/test_metrics.json` | Test evaluation metrics |
| `reports/confusion_matrix_test.png` | Test confusion matrix |
| `reports/pr_curve_test.png` | Precision-recall curve |
| `reports/calibration_test.png` | Model calibration plot |
| `reports/shap_summary.png` | Global SHAP explanation |
| `reports/shap_bar.png` | SHAP feature importance |
| `reports/drift_report.html` | Interactive data drift report |
| `mlflow.db` | MLflow tracking database, when using the SQLite backend |

## 15. Future Improvements

Possible extensions to this project include:

- Deploy the backend and frontend to cloud hosting platforms.
- Add user authentication and role-based dashboard access.
- Store prediction history in a database.
- Add historical churn analytics and customer segmentation.
- Introduce automated model retraining when significant data drift is detected.
- Add monitoring for API latency and prediction performance.
- Add automated deployment through a CI/CD pipeline.

## 16. Conclusion

This project demonstrates an end-to-end machine learning and MLOps workflow for customer churn prediction.

It combines data exploration, preprocessing, model comparison, hyperparameter tuning, business-oriented threshold optimization, model explainability, experiment tracking, drift monitoring, API development, automated testing, and containerization.

The React dashboard provides an accessible interface for interacting with the trained model and understanding its predictions, while the FastAPI backend provides a structured and validated prediction service.

The overall solution demonstrates how a machine learning model can be developed, evaluated, explained, served through an API, and presented through an interactive dashboard.