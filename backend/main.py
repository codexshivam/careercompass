from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import math
import os
import time
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
# Credentials must come from backend/.env only. Never hardcode them here.
SAS_BASE_URL = os.getenv("SAS_BASE_URL", "").strip().rstrip("/")
SAS_MODEL_NAME = os.getenv("SAS_MODULE_NAME", "").strip().strip('"').strip("'")
SAS_AUTH_TOKEN = os.getenv("SAS_AUTH_TOKEN", "").strip().strip('"').strip("'")

# Accept either:
#   SAS_AUTH_TOKEN=eyJ...
# or:
#   SAS_AUTH_TOKEN=Bearer eyJ...
if SAS_AUTH_TOKEN.lower().startswith("bearer "):
    SAS_AUTH_TOKEN = SAS_AUTH_TOKEN[7:].strip()

# Circuit breaker: after an auth/network/module failure, skip SAS calls for
# a while instead of repeatedly failing during the ROI calculations.
SAS_COOLDOWN_SECONDS = 300
_sas_disabled_until = 0.0
_sas_last_error = ""


def _disable_sas(reason: str):
    global _sas_disabled_until, _sas_last_error
    if time.time() >= _sas_disabled_until:
        print(
            f"[SAS] {reason} -> using fallback model "
            f"for {SAS_COOLDOWN_SECONDS // 60} min"
        )
    _sas_disabled_until = time.time() + SAS_COOLDOWN_SECONDS
    _sas_last_error = reason


def _sas_is_configured() -> bool:
    """True when the minimum SAS connection settings are present."""
    return bool(SAS_BASE_URL and SAS_MODEL_NAME and SAS_AUTH_TOKEN)


def get_sas_token():
    """
    Returns the SAS bearer token configured in .env.
    """
    if not _sas_is_configured() or time.time() < _sas_disabled_until:
        return None

    return SAS_AUTH_TOKEN


def fallback_prediction(features: FeatureInput) -> float:
    """Local logistic model used when SAS MAS is unavailable."""
    z = (-26.2236 
         + 1.821 * features.maths 
         + 1.3547 * features.dashboard 
         + 1.2639 * features.ai_ml 
         + 0.9961 * features.big_data 
         + 0.609 * features.coding)
    return 1 / (1 + math.exp(-z))


def get_sas_prediction(features: FeatureInput, token: str):
    """
    Calls the SAS Viya Micro Analytic Service (MAS) REST API.

    Returns:
        (probability, source)
        source is "sas" when MAS successfully scored the request,
        otherwise "fallback".
    """
    if not token or time.time() < _sas_disabled_until:
        return fallback_prediction(features), "fallback"

    # Quote the module name as one URL path segment. This protects module
    # names containing spaces or other URL-reserved characters.
    from urllib.parse import quote

    module_name = quote(SAS_MODEL_NAME, safe="")
    url = (
        f"{SAS_BASE_URL}/microanalyticScore/modules/"
        f"{module_name}/steps/score"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": (
            "application/vnd.sas.microanalytic.module.step.input+json"
        ),
        "Accept": (
            "application/vnd.sas.microanalytic.module.step.output+json"
        ),
    }

    payload = {
        "inputs": [
            {"name": "math", "value": features.maths},
            {"name": "dash", "value": features.dashboard},
            {"name": "aiml", "value": features.ai_ml},
            {"name": "big", "value": features.big_data},
            {"name": "code", "value": features.coding},
        ]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code in (401, 403):
            _disable_sas(
                f"SAS rejected the token (HTTP {response.status_code}). "
                "Check SAS_AUTH_TOKEN or SAS username/password."
            )
            return fallback_prediction(features), "fallback"

        if response.status_code == 404:
            _disable_sas(
                f"SAS module '{SAS_MODEL_NAME}' was not found "
                "in Micro Analytic Service (HTTP 404). "
                "Check SAS_MODULE_NAME."
            )
            return fallback_prediction(features), "fallback"

        if not response.ok:
            # Keep diagnostics short and avoid logging credentials.
            body = response.text[:500].replace("\n", " ")
            _disable_sas(
                f"SAS scoring failed (HTTP {response.status_code}): {body}"
            )
            return fallback_prediction(features), "fallback"

        try:
            result = response.json()
        except ValueError:
            _disable_sas("SAS scoring returned a non-JSON response")
            return fallback_prediction(features), "fallback"

        outputs = result.get("outputs", [])

        for out in outputs:
            name = str(out.get("name", "")).upper()

            # Common SAS model probability output names.
            if name == "EM_EVENTPROBABILITY" or (
                name.startswith("P_") and name.endswith("1")
            ):
                value = float(out.get("value", 0.0))

                # Guard against an invalid probability from SAS.
                if not 0.0 <= value <= 1.0:
                    _disable_sas(
                        f"SAS returned an invalid probability: {value}"
                    )
                    return fallback_prediction(features), "fallback"

                # Successful SAS call: clear the previous diagnostic.
                global _sas_last_error
                _sas_last_error = ""
                return value, "sas"

        output_names = [
            str(out.get("name", "")) for out in outputs[:20]
        ]
        _disable_sas(
            "SAS response had no EM_EVENTPROBABILITY / P_*1 output. "
            f"Returned outputs: {output_names}"
        )
        return fallback_prediction(features), "fallback"

    except requests.RequestException as e:
        _disable_sas(f"SAS scoring request failed: {e}")
        return fallback_prediction(features), "fallback"
    except (TypeError, ValueError) as e:
        _disable_sas(f"Invalid SAS scoring response: {e}")
        return fallback_prediction(features), "fallback"


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Career Compass SAS Model API",
        "sas_health": "/api/health/sas",
    }


@app.get("/api/health/sas")
def sas_health():
    """Shows SAS configuration/status without exposing credentials."""
    return {
        "configured": bool(SAS_BASE_URL and SAS_MODEL_NAME and SAS_AUTH_TOKEN),
        "base_url_configured": bool(SAS_BASE_URL),
        "module_name_configured": bool(SAS_MODEL_NAME),
        "auth_method": "access_token" if SAS_AUTH_TOKEN else None,
        "sas_active": time.time() >= _sas_disabled_until,
        "cooldown_seconds_left": max(
            0, int(_sas_disabled_until - time.time())
        ),
        "last_error": _sas_last_error or None,
    }



@app.post("/predict/promotion")
async def predict_promotion(features: FeatureInput):
    # Fetch token once per request to avoid multiple authentication calls during ROI calculation
    token = get_sas_token()

    # 1. Base Probability Calculation via SAS API
    base_prob, source = get_sas_prediction(features, token)
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
            new_prob, _ = get_sas_prediction(hypo_features, token)
            delta = int(round(new_prob * 100)) - percentage
            
            if delta > best_delta:
                best_delta = delta
                best_skill = skill_names[i]

    return {
        "probability": base_prob,
        "percentage": percentage,
        "verdict": verdict,
        "roi_skill": best_skill,
        "roi_delta": best_delta,
        "source": source
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

