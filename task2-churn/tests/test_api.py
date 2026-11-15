import copy

VALID = {"gender": "Female", "SeniorCitizen": 0, "Partner": "No", "Dependents": "No", "tenure": 3,
         "PhoneService": "Yes", "InternetService": "Fiber optic", "OnlineSecurity": "No", "TechSupport": "No",
         "StreamingTV": "Yes", "Contract": "Month-to-month", "PaperlessBilling": "Yes",
         "PaymentMethod": "Electronic check", "MonthlyCharges": 89.5, "TotalCharges": 268.5}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["model_loaded"] is True


def test_predict_valid(client):
    r = client.post("/predict", json=VALID)
    assert r.status_code == 200
    b = r.json()
    assert 0.0 <= b["churn_probability"] <= 1.0
    assert b["churn_label"] in ("Yes", "No")
    assert (b["churn_label"] == "Yes") == (b["churn_probability"] >= b["threshold"])
    assert len(b["top_reasons"]) == 3 and {"feature", "impact", "direction"} <= set(b["top_reasons"][0])


def test_invalid_category_rejected(client):
    bad = {**VALID, "Contract": "Weekly"}
    assert client.post("/predict", json=bad).status_code == 422


def test_negative_tenure_rejected(client):
    assert client.post("/predict", json={**VALID, "tenure": -5}).status_code == 422


def test_missing_required_field_rejected(client):
    bad = copy.deepcopy(VALID); bad.pop("tenure")
    assert client.post("/predict", json=bad).status_code == 422


def test_extra_field_rejected(client):
    assert client.post("/predict", json={**VALID, "customerID": "X1"}).status_code == 422


def test_edge_missing_charges_ok(client):  # charges are optional -> imputed
    r = client.post("/predict", json={**VALID, "MonthlyCharges": None, "TotalCharges": None})
    assert r.status_code == 200


def test_edge_zero_tenure(client):
    r = client.post("/predict", json={**VALID, "tenure": 0, "TotalCharges": 0})
    assert r.status_code == 200


def test_risky_profile_scores_higher_than_loyal_profile(client):
    loyal = {**VALID, "tenure": 70, "Contract": "Two year", "MonthlyCharges": 40.0, "TotalCharges": 2800.0,
             "OnlineSecurity": "Yes", "TechSupport": "Yes", "PaymentMethod": "Credit card"}
    p_risky = client.post("/predict", json=VALID).json()["churn_probability"]
    p_loyal = client.post("/predict", json=loyal).json()["churn_probability"]
    assert p_risky > p_loyal
