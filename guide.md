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
The backend is now configured to call the live **SAS Viya Micro Analytic Service (MAS)** directly, passing the user's slider values as a JSON payload and retrieving the modeled probability.

To connect it to your live SAS environment, create a `.env` file inside the `backend/` directory:

**File:** `backend/.env`
```env
SAS_BASE_URL=https://<your-sas-viya-server>.com
SAS_USERNAME=your_username
SAS_PASSWORD=your_password
SAS_MODULE_NAME=your_published_model_name
```

**How it works during a Hackathon Demo:**
- The backend automatically authenticates via `/SASLogon/oauth/token` using your `SAS_USERNAME` and `SAS_PASSWORD`, retrieving a secure Bearer token on the fly.
- It restructures the incoming JSON input into the exact array format required by SAS MAS (`{"name": "math", "value": ...}`).
- It sends the request to SAS and parses the `EM_EVENTPROBABILITY` output.
- **Fail-safe Fallback:** If the API fails, times out, or you haven't set up the `.env` variables, it will automatically fallback to a local mathematical formula (`fallback_prediction`). This ensures your UI **never crashes** during your presentation!
- **Dynamic ROI:** The backend calculates the Skill ROI by repeatedly querying the SAS model under the hood to find the best +0.5 delta, giving you true real-time SAS intelligence!

## 2. Managing Salary & Career Ladder Data
The Salary Estimator uses baseline metrics, role premiums, and experience multipliers.

**File:** `src/pages/Salary.tsx`
**Variable:** `salary` (inside the `useMemo` hook)

Update the dictionaries if market data shifts:
```typescript
const premiums: Record<string, number> = { DA: -3.21, BA: -1.3, DE: 1.85, DS: 3.53, MLE: 0, ARCH: 10.95 }
const seniorBumps: Record<string, number> = { DA: 0.79, BA: 0.72, DE: 2.57, DS: 5.1, MLE: 2.5, ARCH: 0 }
// Update the baseline scalar (11.2) and experience multiplier (1.5115) here
```

## 3. Editing Copy and Data Constants
All hardcoded labels, dropdown options, and copy content are centralised in the constants file.

**File:** `src/data/constants.ts`

- `competencyFields`: The 5 technical pillars used in the Simulator. Formatted as `[Name, Low Label, Mid Label, High Label, Default Value]`.
- `roles`: The job titles populated in the Salary Estimator dropdown.
- `matrixItems`: The Skill Gap / Market Demand Matrix cards content.
- `personas`: The Senior Leadership Personas clustering results.

## 4. UI/UX Design Configuration
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
