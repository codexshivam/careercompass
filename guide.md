# Career Compass - Configuration Guide

This guide explains how to manage settings, update the underlying SAS models, and configure data for the Career Compass web application.

## 1. Running the FastAPI Backend (SAS Model Integration)
The core logic for predicting the probability of a high salary hike now runs on a Python FastAPI backend. This allows you to integrate the actual SAS Decision Tree model via an API instead of hardcoding logic in the frontend.

### Setup Backend
Open a terminal and navigate to the `backend` directory:
```bash
cd backend
pip install -r requirements.txt
```

### Start the Server
Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```
The backend will run on `http://127.0.0.1:8000`. 

### Integrating the Live SAS REST API (Micro Analytic Service)
The backend is configured to call the live **SAS Viya Micro Analytic Service (MAS)** directly, passing the user's slider values as a JSON payload and retrieving the modeled probability.

To connect it to your live SAS environment, create a `.env` file inside the `backend/` directory:

**File:** `backend/.env`
```env
SAS_BASE_URL=https://<your-sas-viya-server>.com
SAS_MODULE_NAME=your_published_model_name
SAS_AUTH_TOKEN=eyJ...your_bearer_token...
```

**How it works during a Hackathon Demo:**
- The backend attaches `Authorization: Bearer <SAS_AUTH_TOKEN>` to all scoring requests.
- It restructures the incoming JSON input into the exact array format required by SAS MAS (`{"name": "math", "value": ...}`).
- It sends the request to SAS and parses the `EM_EVENTPROBABILITY` output.
- **Fail-safe Fallback:** If the token is not provided, expired, or the SAS API times out, it automatically falls back to the local model formula (`fallback_prediction`). This ensures your UI **never crashes** during your presentation!
- **Dynamic ROI:** The backend calculates the Skill ROI by repeatedly querying the SAS model under the hood to find the best +0.5 delta, giving you true real-time SAS intelligence!


## 2. Managing Data, Configuration & Endpoints (All in Backend)
All business data, configuration parameters, metadata, and formulas are centralized and served directly by the FastAPI backend (`backend/main.py`). The frontend contains **no static sample data arrays**.

### Key Endpoints in `backend/main.py`:
- `GET /api/meta/competencies`: Provides the 5 technical competency pillars, labels, and defaults for the Simulator.
- `GET /api/salary/config`: Serves the list of career roles and the Seniority Premium comparison chart data.
- `POST /api/salary/estimate`: Computes estimated annual compensation based on target role, experience, seniority, and location tier.
- `GET /api/matrix`: Serves the market demand vs. promotion impact skill matrix cards.
- `GET /api/personas`: Serves the 4 leadership success personas.
- `POST /predict/promotion`: Executes model prediction (SAS REST API with automated fail-safe calculation) and returns probability, verdict, and the optimal +0.5 upskilling ROI recommendation.

To update compensation baseline numbers, role tiers, personas, or matrix items, edit `backend/main.py`. Any changes in the backend will immediately reflect on the frontend upon page refresh.

## 3. UI/UX Design Configuration
Colors, breakpoints, and CSS layouts are managed globally via standard CSS variables.

**File:** `src/App.css`

At the top of the file, you can manage the core theme colors:
```css
:root { 
  --ink: #0a0a0a;   /* Primary dark color for text/bars/active states */
  --muted: #71717a; /* Secondary text and disabled states */
  --line: #e4e4e7;  /* Borders and dividers */
  --low: #f6f2f7;   /* Backgrounds for cards and inputs */
}
```
Fonts are configured in `src/index.css` via a Google Fonts import (`Geist` and `JetBrains Mono`).

## 5. Development Commands
The project is built with Vite + React + TypeScript.

- **Start Local Server:** `npm run dev`
- **Build for Production:** `npm run build`
- **Lint Code:** `npm run lint`
