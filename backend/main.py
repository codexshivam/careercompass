from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sas_engine import evaluate_promotion

app = FastAPI(title="Career Compass SAS Model Backend")

# Enable CORS for React frontend (localhost:5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FeatureInput(BaseModel):
    dashboard: float
    maths: float
    ai_ml: float
    big_data: float
    coding: float


class SalaryInput(BaseModel):
    role: str
    experience: float
    senior: bool
    location: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Career Compass Backend",
        "engine": "SAS Score Code Engine",
        "version": "1.0.0"
    }


# ==========================================
# 1. SAS MODEL PREDICTION ENDPOINT
# ==========================================
@app.post("/predict/promotion")
def predict_promotion(data: FeatureInput):
    """
    Executes the SAS model scoring directly using the cleaned SAS scoring rules.
    Returns probability, percentage, verdict, and dynamic upskilling ROI.
    """
    return evaluate_promotion(
        dashboard=data.dashboard,
        maths=data.maths,
        ai_ml=data.ai_ml,
        big_data=data.big_data,
        coding=data.coding
    )


# ==========================================
# 2. COMPETENCY METADATA ENDPOINT
# ==========================================
@app.get("/api/meta/competencies")
def get_competencies():
    return [
        {
            "id": "dash",
            "name": "Dashboard & Storytelling",
            "low": "Basic visual",
            "mid": "Functional",
            "high": "C-Suite Narrative",
            "default": 4.0
        },
        {
            "id": "math",
            "name": "Maths & Statistical Rigor",
            "low": "Formulas",
            "mid": "Regression",
            "high": "Causal Inference",
            "default": 4.0
        },
        {
            "id": "aiml",
            "name": "AI & Machine Learning",
            "low": "Baselines",
            "mid": "Feature Eng.",
            "high": "Production GenAI/NLP",
            "default": 4.0
        },
        {
            "id": "big",
            "name": "Big Data Architecture",
            "low": "Local",
            "mid": "Distributed SQL",
            "high": "Spark / CAS Tuning",
            "default": 3.5
        },
        {
            "id": "code",
            "name": "Core Programming (Python/SQL/SAS)",
            "low": "Scripting",
            "mid": "Clean Modular",
            "high": "Enterprise CI/CD",
            "default": 4.2
        }
    ]


# ==========================================
# 3. SALARY CALCULATOR ENDPOINTS
# ==========================================
@app.get("/api/salary/config")
def get_salary_config():
    return {
        "roles": [
            {"code": "DA", "label": "Data Analyst (Junior Base: ₹5.0L)"},
            {"code": "BA", "label": "Business Analyst (Junior Base: ₹8.3L)"},
            {"code": "DE", "label": "Data Engineer (Junior Base: ₹10.9L)"},
            {"code": "DS", "label": "Data Scientist (Junior Base: ₹12.8L)"},
            {"code": "MLE", "label": "Machine Learning Engineer (Junior Base: ₹9.1L)"},
            {"code": "ARCH", "label": "Data Architect (Senior Base: ₹24.2L)"}
        ],
        "premiumsChart": [
            {"role": "Data Science", "premium": 5.1},
            {"role": "Data Engineering", "premium": 2.57},
            {"role": "Data Analyst", "premium": 0.79},
            {"role": "Business Analyst", "premium": 0.72}
        ]
    }


@app.post("/api/salary/estimate")
def estimate_salary(data: SalaryInput):
    premiums = {"DA": -3.21, "BA": -1.30, "DE": 1.85, "DS": 3.53, "MLE": 0.0, "ARCH": 10.95}
    senior_bumps = {"DA": 0.79, "BA": 0.72, "DE": 2.57, "DS": 5.10, "MLE": 2.50, "ARCH": 0.0}

    exp_add = 1.5115 * data.experience
    role_premium = premiums.get(data.role, 0.0)
    bump = senior_bumps.get(data.role, 0.0) if data.senior else 0.0

    total = 11.20 + exp_add + role_premium + bump
    if data.location == "regional" and data.experience < 5:
        total *= 0.78

    return {
        "total": round(max(3.5, total), 1),
        "expAdd": round(exp_add, 1),
        "premium": round(role_premium, 1),
        "bump": round(bump, 1)
    }


# ==========================================
# 4. SKILL MATRIX & PERSONAS ENDPOINTS
# ==========================================
@app.get("/api/matrix")
def get_matrix():
    return [
        {
            "tag": "HIGH DIFFERENTIATOR",
            "impact": "TOP IMPACT",
            "title": "Data Visualization & Storytelling",
            "demand": "12% (Moderate)",
            "impactRating": "Very High",
            "description": "Often under-emphasized in job descriptions, but one of the strongest internal differentiators for executive visibility and top-tier promotions."
        },
        {
            "tag": "CORE FOUNDATION",
            "impact": "HIGH DEMAND & PAY",
            "title": "Maths, Statistics & AI/ML Modeling",
            "demand": "16% (Stats) / 14% (AI)",
            "impactRating": "High Multiplier",
            "description": "Deep mathematical and statistical intuition remains the primary technical driver for advancing into senior data science positions."
        },
        {
            "tag": "SUPPORTING SKILL",
            "impact": "MODERATE ROI",
            "title": "Big Data Infrastructure (Hadoop/Spark)",
            "demand": "13%",
            "impactRating": "Moderate",
            "description": "Essential for infrastructure and engineering workflows, but secondary for promotion velocity compared to core modeling and communication."
        },
        {
            "tag": "TABLE STAKES",
            "impact": "BASELINE",
            "title": "Coding (Python, SQL, SAS, R)",
            "demand": "44% (Most Common)",
            "impactRating": "Baseline Requirement",
            "description": "Mandatory hygiene skill required across all roles; universal baseline expectation that alone does not drive top differentiation."
        }
    ]


@app.get("/api/personas")
def get_personas():
    return [
        {
            "id": "01",
            "badge": "96% Win Rate",
            "title": "The Driven Explorer",
            "description": "Combines rigorous execution discipline with high curiosity and decisive stakeholder leadership."
        },
        {
            "id": "02",
            "badge": "71% Win Rate",
            "title": "The Diplomatic Champion",
            "description": "Exceptional relationship building and stakeholder empathy; highly effective when paired with deep technical delivery anchors."
        },
        {
            "id": "03",
            "badge": "39% Win Rate",
            "title": "The Quiet Specialist",
            "description": "Technically thorough and detail-oriented, but encounters resistance in high-ambiguity client escalations."
        },
        {
            "id": "04",
            "badge": "18% Win Rate",
            "title": "The Developing Contributor",
            "description": "Building a strong technical foundation while developing the communication habits that unlock broader influence."
        }
    ]