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
SAS_BASE_URL = os.getenv("SAS_BASE_URL", "https://your-sas-viya-server.com")
SAS_MODEL_NAME = os.getenv("SAS_MODULE_NAME", "career_compass_model")
SAS_USERNAME = os.getenv("SAS_USERNAME", "your_username")
SAS_PASSWORD = os.getenv("SAS_PASSWORD", "your_password")

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
