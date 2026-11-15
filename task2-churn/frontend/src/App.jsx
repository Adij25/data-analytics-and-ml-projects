
import { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  ArrowUpRight,
  BarChart3,
  Brain,
  CheckCircle2,
  FileText,
  Gauge,
  LayoutDashboard,
  Loader2,
  Menu,
  RefreshCw,
  ShieldCheck,
  Users,
  X,
  Zap
} from "lucide-react";
import "./App.css";

const initialCustomer = {
  gender: "Female",
  SeniorCitizen: "0",
  Partner: "No",
  Dependents: "No",
  tenure: "3",
  PhoneService: "Yes",
  InternetService: "Fiber optic",
  OnlineSecurity: "No",
  TechSupport: "No",
  StreamingTV: "Yes",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: "89.5",
  TotalCharges: "268.5"
};

const fieldGroups = [
  {
    title: "Personal information",
    fields: [
      { name: "gender", label: "Gender", type: "select", options: ["Female", "Male"] },
      { name: "SeniorCitizen", label: "Senior citizen", type: "select", options: ["0", "1"] },
      { name: "Partner", label: "Has partner", type: "select", options: ["Yes", "No"] },
      { name: "Dependents", label: "Has dependents", type: "select", options: ["Yes", "No"] }
    ]
  },
  {
    title: "Subscription details",
    fields: [
      { name: "tenure", label: "Tenure (months)", type: "number", min: 0, max: 120 },
      { name: "PhoneService", label: "Phone service", type: "select", options: ["Yes", "No"] },
      { name: "InternetService", label: "Internet service", type: "select", options: ["DSL", "Fiber optic", "No"] },
      { name: "OnlineSecurity", label: "Online security", type: "select", options: ["Yes", "No"] },
      { name: "TechSupport", label: "Tech support", type: "select", options: ["Yes", "No"] },
      { name: "StreamingTV", label: "Streaming TV", type: "select", options: ["Yes", "No"] },
      { name: "Contract", label: "Contract type", type: "select", options: ["Month-to-month", "One year", "Two year"] },
      { name: "PaperlessBilling", label: "Paperless billing", type: "select", options: ["Yes", "No"] },
      { name: "PaymentMethod", label: "Payment method", type: "select", options: ["Electronic check", "Mailed check", "Bank transfer", "Credit card"] }
    ]
  },
  {
    title: "Billing information",
    fields: [
      { name: "MonthlyCharges", label: "Monthly charges", type: "number", min: 0, max: 500, step: "any" },
      { name: "TotalCharges", label: "Total charges", type: "number", min: 0, max: 100000, step: "any" }
    ]
  }
];

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [health, setHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [customer, setCustomer] = useState(initialCustomer);
  const [prediction, setPrediction] = useState(null);
  const [predictLoading, setPredictLoading] = useState(false);
  const [error, setError] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);

  const checkHealth = async () => {
    setHealthLoading(true);
    try {
      const response = await fetch("/health");
      if (!response.ok) throw new Error("Unable to check API health.");
      const data = await response.json();
      setHealth(data);
    } catch (err) {
      setHealth({
        status: "offline",
        model_loaded: false,
        threshold: null
      });
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const updateCustomer = (name, value) => {
    setCustomer((previous) => ({ ...previous, [name]: value }));
  };

  const handlePrediction = async (event) => {
    event.preventDefault();
    setError("");
    setPrediction(null);

    if (!health?.model_loaded) {
      setError("The ML model is not loaded. Please check your FastAPI backend.");
      return;
    }

    const payload = {
      ...customer,
      SeniorCitizen: Number(customer.SeniorCitizen),
      tenure: Number(customer.tenure),
      MonthlyCharges:
        customer.MonthlyCharges.trim() === ""
          ? null
          : Number(customer.MonthlyCharges),
      TotalCharges:
        customer.TotalCharges.trim() === ""
          ? null
          : Number(customer.TotalCharges)
    };

    setPredictLoading(true);

    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : "Prediction request failed. Please check the entered values.";
        throw new Error(detail);
      }

      setPrediction(data);
      setActivePage("Predict Churn");
    } catch (err) {
      setError(err.message || "Something went wrong while predicting churn.");
    } finally {
      setPredictLoading(false);
    }
  };

  const navigation = [
    { label: "Overview", icon: LayoutDashboard },
    { label: "Predict Churn", icon: Users },
    { label: "Data Drift Report", icon: Activity },
    { label: "Model Insights", icon: Brain }
  ];

  const goToPage = (page) => {
    setActivePage(page);
    setMobileMenu(false);
  };

  const probability = prediction
    ? Math.round(prediction.churn_probability * 100)
    : null;

  return (
    <div className="app-shell">
      {mobileMenu && (
        <button
          className="mobile-overlay"
          aria-label="Close navigation"
          onClick={() => setMobileMenu(false)}
        />
      )}

      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><Brain size={23} /></div>
          <div>
            <h2>Churn<span>IQ</span></h2>
            <p>Prediction platform</p>
          </div>
          <button className="mobile-close" onClick={() => setMobileMenu(false)}>
            <X size={20} />
          </button>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav className="navigation">
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${activePage === label ? "active" : ""}`}
              onClick={() => goToPage(label)}
            >
              <Icon size={19} />
              <span>{label}</span>
              {activePage === label && <span className="active-dot" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <div className={`status-dot ${health?.model_loaded ? "online" : "offline"}`} />
            <div>
              <strong>ML Model</strong>
              <span>{healthLoading ? "Checking..." : health?.model_loaded ? "Operational" : "Unavailable"}</span>
            </div>
          </div>
          <p className="sidebar-version">Customer Churn Analytics · v1.0</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" onClick={() => setMobileMenu(true)}>
              <Menu size={22} />
            </button>
            <div>
              <p className="breadcrumb">Workspace / <span>{activePage}</span></p>
              <h1>{activePage}</h1>
            </div>
          </div>
          <div className="topbar-right">
            <div className={`api-indicator ${health?.model_loaded ? "connected" : "disconnected"}`}>
              <span className="status-dot" />
              {healthLoading ? "Checking API" : health?.model_loaded ? "API Connected" : "API Offline"}
            </div>
            <button className="icon-button" onClick={checkHealth} title="Refresh API status">
              <RefreshCw size={18} />
            </button>
            <div className="avatar">CI</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === "Overview" && (
            <Overview
              health={health}
              healthLoading={healthLoading}
              prediction={prediction}
              onNavigate={goToPage}
              onRefresh={checkHealth}
            />
          )}

          {activePage === "Predict Churn" && (
            <section>
              <div className="section-intro">
                <div>
                  <p className="eyebrow">MACHINE LEARNING</p>
                  <h2>Customer churn prediction</h2>
                  <p>Enter customer details to estimate their likelihood of leaving.</p>
                </div>
                <div className="model-chip"><ShieldCheck size={16} /> XGBoost pipeline</div>
              </div>

              <div className="prediction-layout">
                <form className="customer-form" onSubmit={handlePrediction}>
                  {fieldGroups.map((group) => (
                    <div className="form-section" key={group.title}>
                      <h3>{group.title}</h3>
                      <div className="form-grid">
                        {group.fields.map((field) => (
                          <label className="form-field" key={field.name}>
                            <span>{field.label}</span>
                            {field.type === "select" ? (
                              <select
                                value={customer[field.name]}
                                onChange={(e) => updateCustomer(field.name, e.target.value)}
                              >
                                {field.options.map((option) => (
                                  <option key={option} value={option}>{option}</option>
                                ))}
                              </select>
                            ) : (
                              <input
                                type="number"
                                min={field.min}
                                max={field.max}
                                step={field.step || 1}
                                value={customer[field.name]}
                                onChange={(e) => updateCustomer(field.name, e.target.value)}
                              />
                            )}
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}

                  {error && (
                    <div className="error-message">
                      <AlertCircle size={18} />
                      <span>{error}</span>
                    </div>
                  )}

                  <div className="form-actions">
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => {
                        setCustomer(initialCustomer);
                        setPrediction(null);
                        setError("");
                      }}
                    >
                      Reset form
                    </button>
                    <button
                      type="submit"
                      className="primary-button"
                      disabled={predictLoading || !health?.model_loaded}
                    >
                      {predictLoading ? <Loader2 className="spin" size={18} /> : <Zap size={18} />}
                      {predictLoading ? "Predicting..." : "Predict churn"}
                    </button>
                  </div>
                  {!health?.model_loaded && !healthLoading && (
                    <p className="form-note">Prediction is disabled because the backend model is unavailable.</p>
                  )}
                </form>

                <PredictionResult prediction={prediction} />
              </div>
            </section>
          )}

          {activePage === "Data Drift Report" && (
            <section>
              <div className="section-intro">
                <div>
                  <p className="eyebrow">MODEL MONITORING</p>
                  <h2>Data drift report</h2>
                  <p>Your existing drift analysis report, displayed inside the dashboard.</p>
                </div>
                <a
                  className="secondary-button link-button"
                  href="/reports/drift_report.html"
                  target="_blank"
                  rel="noreferrer"
                >
                  <ArrowUpRight size={17} /> Open report separately
                </a>
              </div>
              <div className="report-frame">
                <iframe
                  src="/reports/drift_report.html"
                  title="Customer churn data drift report"
                />
              </div>
            </section>
          )}

          {activePage === "Model Insights" && (
            <section>
              <div className="section-intro">
                <div>
                  <p className="eyebrow">MODEL EXPLAINABILITY</p>
                  <h2>Model insights</h2>
                  <p>Understand the factors influencing the latest customer prediction.</p>
                </div>
              </div>
              {prediction ? (
                <div className="insights-card">
                  <h3>Latest prediction drivers</h3>
                  <p className="muted-text">
                    These are the top contribution values returned by your backend for the latest prediction.
                  </p>
                  {prediction.top_reasons?.length ? (
                    prediction.top_reasons.map((reason, index) => (
                      <div className="reason-row" key={`${reason.feature}-${index}`}>
                        <div className="reason-number">{index + 1}</div>
                        <div className="reason-info">
                          <strong>{reason.feature}</strong>
                          <span>{reason.direction}</span>
                        </div>
                        <div className={`impact-value ${reason.impact > 0 ? "risk-up" : "risk-down"}`}>
                          {reason.impact > 0 ? "+" : ""}{reason.impact.toFixed(4)}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="empty-state">No feature contribution details were returned for this model.</p>
                  )}
                </div>
              ) : (
                <div className="empty-panel">
                  <Brain size={36} />
                  <h3>No prediction available yet</h3>
                  <p>Run a customer churn prediction to see its explanation here.</p>
                  <button className="primary-button" onClick={() => goToPage("Predict Churn")}>
                    Predict a customer
                  </button>
                </div>
              )}
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

function Overview({ health, healthLoading, prediction, onNavigate, onRefresh }) {
  return (
    <section>
      <div className="welcome-row">
        <div>
          <p className="eyebrow">CUSTOMER ANALYTICS</p>
          <h2>Welcome to your churn dashboard</h2>
          <p>Monitor model availability and predict customer churn risk.</p>
        </div>
        <button className="primary-button" onClick={() => onNavigate("Predict Churn")}>
          <Zap size={18} /> New prediction
        </button>
      </div>

      <div className="metric-grid">
        <MetricCard
          icon={<Activity size={20} />}
          label="API status"
          value={healthLoading ? "Checking" : health?.model_loaded ? "Online" : "Offline"}
          note="FastAPI service"
          tone={health?.model_loaded ? "green" : "orange"}
        />
        <MetricCard
          icon={<Brain size={20} />}
          label="ML model"
          value={healthLoading ? "Checking" : health?.model_loaded ? "Loaded" : "Not loaded"}
          note="Prediction pipeline"
          tone={health?.model_loaded ? "blue" : "orange"}
        />
        <MetricCard
          icon={<Gauge size={20} />}
          label="Decision threshold"
          value={health?.threshold != null ? `${(health.threshold * 100).toFixed(1)}%` : "—"}
          note="Loaded from model metadata"
          tone="purple"
        />
        <MetricCard
          icon={<BarChart3 size={20} />}
          label="Latest prediction"
          value={prediction ? prediction.churn_label === "Yes" ? "Churn risk" : "No churn" : "—"}
          note={prediction ? "Most recent customer result" : "No predictions yet"}
          tone="blue"
        />
      </div>

      <div className="overview-grid">
        <div className="panel model-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">SYSTEM HEALTH</p>
              <h3>Model availability</h3>
            </div>
            <button className="icon-button" onClick={onRefresh} title="Refresh status">
              <RefreshCw size={17} />
            </button>
          </div>
          <div className="health-banner">
            <div className={`health-icon ${health?.model_loaded ? "healthy" : "unhealthy"}`}>
              {health?.model_loaded ? <CheckCircle2 size={24} /> : <AlertCircle size={24} />}
            </div>
            <div>
              <strong>{health?.model_loaded ? "Model is ready" : "Model unavailable"}</strong>
              <p>{healthLoading ? "Checking backend..." : health?.model_loaded ? "The API is ready to receive predictions." : "Start the FastAPI server and verify model loading."}</p>
            </div>
          </div>
          <div className="health-detail">
            <span>Service status</span>
            <strong>{health?.status || "Unknown"}</strong>
          </div>
          <div className="health-detail">
            <span>Prediction endpoint</span>
            <strong>/predict</strong>
          </div>
          <div className="health-detail">
            <span>Health endpoint</span>
            <strong>/health</strong>
          </div>
        </div>

        <div className="panel quick-panel">
          <p className="eyebrow">QUICK ACCESS</p>
          <h3>Explore your project</h3>
          <button className="quick-link" onClick={() => onNavigate("Predict Churn")}>
            <div className="quick-icon blue"><Users size={20} /></div>
            <div><strong>Predict customer churn</strong><span>Submit customer details to the ML model</span></div>
            <ArrowUpRight size={18} />
          </button>
          <button className="quick-link" onClick={() => onNavigate("Data Drift Report")}>
            <div className="quick-icon purple"><FileText size={20} /></div>
            <div><strong>View data drift report</strong><span>Review your existing monitoring report</span></div>
            <ArrowUpRight size={18} />
          </button>
          <button className="quick-link" onClick={() => onNavigate("Model Insights")}>
            <div className="quick-icon green"><Brain size={20} /></div>
            <div><strong>Model explanations</strong><span>Understand prediction drivers</span></div>
            <ArrowUpRight size={18} />
          </button>
        </div>
      </div>

      {prediction && (
        <div className="panel latest-panel">
          <div>
            <p className="eyebrow">LATEST RESULT</p>
            <h3>Most recent customer prediction</h3>
            <p className="muted-text">The result returned by your trained model.</p>
          </div>
          <div className="latest-result">
            <span className={`result-pill ${prediction.churn_label === "Yes" ? "high-risk" : "low-risk"}`}>
              {prediction.churn_label === "Yes" ? "Churn predicted" : "No churn predicted"}
            </span>
            <strong>{(prediction.churn_probability * 100).toFixed(1)}%</strong>
          </div>
        </div>
      )}
    </section>
  );
}

function MetricCard({ icon, label, value, note, tone }) {
  return (
    <div className="metric-card">
      <div className={`metric-icon ${tone}`}>{icon}</div>
      <p>{label}</p>
      <h3>{value}</h3>
      <span>{note}</span>
    </div>
  );
}

function PredictionResult({ prediction }) {
  if (!prediction) {
    return (
      <div className="result-panel result-placeholder">
        <div className="placeholder-icon"><Gauge size={30} /></div>
        <h3>Prediction results</h3>
        <p>Complete the customer form and select Predict churn to see the model's result here.</p>
        <div className="placeholder-note">
          <ShieldCheck size={17} />
          Results are generated by your trained ML pipeline.
        </div>
      </div>
    );
  }

  const percentage = Math.round(prediction.churn_probability * 100);
  const churn = prediction.churn_label === "Yes";

  return (
    <div className="result-panel">
      <p className="eyebrow">PREDICTION OUTPUT</p>
      <h3>Customer risk assessment</h3>
      <div className={`prediction-status ${churn ? "risk-status" : "safe-status"}`}>
        {churn ? <AlertCircle size={20} /> : <CheckCircle2 size={20} />}
        <span>{churn ? "Churn predicted" : "No churn predicted"}</span>
      </div>

      <div className="probability-area">
        <div
          className={`probability-ring ${churn ? "ring-risk" : "ring-safe"}`}
          style={{ "--probability": `${percentage * 3.6}deg` }}
        >
          <div className="probability-inner">
            <strong>{percentage}%</strong>
            <span>Churn probability</span>
          </div>
        </div>
      </div>

      <div className="result-detail">
        <span>Model probability</span>
        <strong>{prediction.churn_probability.toFixed(4)}</strong>
      </div>
      <div className="result-detail">
        <span>Decision threshold</span>
        <strong>{(prediction.threshold * 100).toFixed(1)}%</strong>
      </div>

      <div className="result-reasons">
        <h4>Top prediction drivers</h4>
        {prediction.top_reasons?.length ? (
          prediction.top_reasons.map((reason, index) => (
            <div className="compact-reason" key={`${reason.feature}-${index}`}>
              <div>
                <strong>{reason.feature}</strong>
                <span>{reason.direction}</span>
              </div>
              <b className={reason.impact > 0 ? "risk-up" : "risk-down"}>
                {reason.impact > 0 ? "+" : ""}{reason.impact.toFixed(3)}
              </b>
            </div>
          ))
        ) : (
          <p className="muted-text">No feature contributions available for this model.</p>
        )}
      </div>
      <p className="result-disclaimer">
        Prediction is based on the model and threshold currently loaded by the API.
      </p>
    </div>
  );
}

export default App;
