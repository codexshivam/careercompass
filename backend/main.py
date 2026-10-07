from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import math
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (for SAS credentials)
load_dotenv()

app = FastAPI(title="Career Compass SAS Model API")

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

# --- SAS REST API CONFIGURATION ---
SAS_BASE_URL = os.getenv("SAS_BASE_URL", "https://viya-4yzi79h1nh.engage.sas.com/")
SAS_MODEL_NAME = os.getenv("SAS_MODULE_NAME", "Forest")
SAS_USERNAME = os.getenv("SAS_USERNAME", "raj@koolkanchatravel.com")
SAS_PASSWORD = os.getenv("SAS_PASSWORD", "Namaste@9864")

def get_sas_token():
    """Generates an OAuth Bearer token from SAS Viya using username and password."""
    if not SAS_USERNAME or SAS_USERNAME == "your_username":
        return None  # Skip if credentials are not set

    auth_url = f"{SAS_BASE_URL}/SASLogon/oauth/token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "password",
        "username": SAS_USERNAME,
        "password": SAS_PASSWORD
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=payload, auth=("sas.cli", ""), timeout=5)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Failed to authenticate with SAS: {e}")
        return None

def fallback_prediction(features: FeatureInput) -> float:
    """Fallback in case SAS REST API is down or misconfigured."""
    z = (-26.2236 
         + 1.821 * features.maths 
         + 1.3547 * features.dashboard 
         + 1.2639 * features.ai_ml 
         + 0.9961 * features.big_data 
         + 0.609 * features.coding)
    return 1 / (1 + math.exp(-z))

def get_sas_prediction(features: FeatureInput, token: str) -> float:
    """
    Calls the SAS Viya Micro Analytic Service (MAS) REST API.
    """
    if not token or "your-sas-viya-server.com" in SAS_BASE_URL:
        return fallback_prediction(features)

    url = f"{SAS_BASE_URL}/microanalyticScore/modules/{SAS_MODEL_NAME}/steps/score"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.sas.microanalytic.module.step.input+json",
        "Accept": "application/vnd.sas.microanalytic.module.step.output+json"
    }
    
    # Payload format required by SAS MAS
    payload = {
        "inputs": [
            {"name": "math", "value": features.maths},
            {"name": "dash", "value": features.dashboard},
            {"name": "aiml", "value": features.ai_ml},
            {"name": "big", "value": features.big_data},
            {"name": "code", "value": features.coding}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        # Extract probability (Looking for EM_EVENTPROBABILITY or P_*1)
        outputs = data.get("outputs", [])
        for out in outputs:
            name = out.get("name", "").upper()
            if name == "EM_EVENTPROBABILITY" or (name.startswith("P_") and name.endswith("1")):
                return float(out.get("value", 0.0))
                
        return fallback_prediction(features)
        
    except Exception as e:
        print(f"SAS REST API Error: {e}")
        return fallback_prediction(features)

@app.post("/predict/promotion")
async def predict_promotion(features: FeatureInput):
    # Fetch token once per request to avoid multiple authentication calls during ROI calculation
    token = get_sas_token()

    # 1. Base Probability Calculation via SAS API
    base_prob = get_sas_prediction(features, token)
    percentage = int(round(base_prob * 100))
    
    # 2. Verdict Logic
    if percentage >= 70:
        verdict = 'High Likelihood Zone'
    elif percentage >= 40:
        verdict = 'Moderate Competitive Zone'
    else:
        verdict = 'Low Probability Zone'
        
    # 3. Upskilling ROI Logic
    skill_names = [
        "Dashboard & Storytelling", 
        "Maths & Statistical Rigor", 
        "AI & Machine Learning", 
        "Big Data Architecture", 
        "Core Programming (Python/SQL/SAS)"
    ]
    current_scores = [
        features.dashboard, 
        features.maths, 
        features.ai_ml, 
        features.big_data, 
        features.coding
    ]
    
    best_delta = 0
    best_skill = None
    
    for i in range(5):
        if current_scores[i] < 5.0:
            hypothetical_scores = current_scores.copy()
            hypothetical_scores[i] = min(5.0, hypothetical_scores[i] + 0.5)
            
            hypo_features = FeatureInput(
                dashboard=hypothetical_scores[0],
                maths=hypothetical_scores[1],
                ai_ml=hypothetical_scores[2],
                big_data=hypothetical_scores[3],
                coding=hypothetical_scores[4]
            )
            
            # Predict with the +0.5 boost reusing the same token
            new_prob = get_sas_prediction(hypo_features, token)
            delta = int(round(new_prob * 100)) - percentage
            
            if delta > best_delta:
                best_delta = delta
                best_skill = skill_names[i]

    return {
        "probability": base_prob,
        "percentage": percentage,
        "verdict": verdict,
        "roi_skill": best_skill,
        "roi_delta": best_delta
    }


class SalaryInput(BaseModel):
    role: str
    experience: float
    senior: bool
    location: str


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


@app.get("/api/salary/config")
def get_salary_config():
    roles = [
        {"code": "DA", "label": "Data Analyst (Junior Base: ₹5.0L)"},
        {"code": "BA", "label": "Business Analyst (Junior Base: ₹8.3L)"},
        {"code": "DE", "label": "Data Engineer (Junior Base: ₹10.9L)"},
        {"code": "DS", "label": "Data Scientist (Junior Base: ₹12.8L)"},
        {"code": "MLE", "label": "Machine Learning Engineer (Junior Base: ₹9.1L)"},
        {"code": "ARCH", "label": "Data Architect (Senior Base: ₹24.2L)"}
    ]
    premiums_chart = [
        {"role": "Data Science", "premium": 5.1},
        {"role": "Data Engineering", "premium": 2.57},
        {"role": "Data Analyst", "premium": 0.79},
        {"role": "Business Analyst", "premium": 0.72}
    ]
    return {
        "roles": roles,
        "premiumsChart": premiums_chart
    }


@app.post("/api/salary/estimate")
def estimate_salary(data: SalaryInput):
    premiums = {"DA": -3.21, "BA": -1.3, "DE": 1.85, "DS": 3.53, "MLE": 0.0, "ARCH": 10.95}
    senior_bumps = {"DA": 0.79, "BA": 0.72, "DE": 2.57, "DS": 5.1, "MLE": 2.5, "ARCH": 0.0}

    exp_add = 1.5115 * data.experience
    role_premium = premiums.get(data.role, 0.0)
    bump = senior_bumps.get(data.role, 0.0) if data.senior else 0.0

    total = 11.2 + exp_add + role_premium + bump
    if data.location == "regional" and data.experience < 5:
        total *= 0.78

    return {
        "total": round(max(3.5, total), 1),
        "expAdd": round(exp_add, 1),
        "premium": round(role_premium, 1),
        "bump": round(bump, 1)
    }


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

