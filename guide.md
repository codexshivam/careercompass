# Career Compass — Production Deployment Guide
## Vercel (Frontend) + Railway (Backend)

> **Project:** Career Compass — Data Science Career Value Chain & Promotion Predictor  
> **Team:** Team Rocket (Chandigarh University)  
> **Production Stack:**  
> • **Frontend:** React + TypeScript + Vite deployed on **Vercel** (Edge CDN)  
> • **Backend:** Python + FastAPI + SAS Score Engine deployed on **Railway**  
> • **Repository:** [github.com/codexshivam/careercompass](https://github.com/codexshivam/careercompass)

---

## 1. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   VERCEL (Frontend CDN)                  │
│             https://careercompass.vercel.app             │
│            (React 18 + Vite + TypeScript)                │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTPS / REST API
                             ▼
┌──────────────────────────────────────────────────────────┐
│                   RAILWAY (Backend App)                  │
│       https://careercompass-backend.up.railway.app       │
│                (FastAPI + Python 3.12)                   │
├──────────────────────────────────────────────────────────┤
│ • /predict/promotion       • /api/salary/estimate        │
│ • /api/meta/competencies   • /api/matrix & /personas     │
├──────────────────────────────────────────────────────────┤
│              SAS MODEL SCORING ENGINE                    │
│               (backend/sas_engine.py)                    │
│   In-memory mathematical evaluation of SAS Viya model    │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Step-by-Step Deployment Instructions

---

### Part 1: Deploy Backend on Railway

Railway will host the Python FastAPI server with automated deployments on every Git push.

1. **Sign in to Railway:**
   Go to [railway.app](https://railway.app) and log in with your GitHub account.

2. **Create a New Project:**
   - Click **+ New Project** → **Deploy from GitHub repo**.
   - Select your repository: `codexshivam/careercompass`.

3. **Configure Service Settings:**
   Once imported, click on the created service card and open the **Settings** tab:
   - **Root Directory:** Set to `backend`
   - **Build Command:** *(Leave empty / auto-detected from requirements.txt)*
   - **Start Command:**
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. **Generate Public Domain:**
   - Under the **Networking** section of the Settings tab, click **Generate Domain**.
   - Copy your public backend URL. It will look like:
     `https://careercompass-production-xxxx.up.railway.app`

5. **Verify Backend Deployment:**
   Open the URL in your browser:
   - `https://your-railway-url.up.railway.app/docs` → Interactive Swagger documentation.
   - `https://your-railway-url.up.railway.app/api/meta/competencies` → Returns competency JSON.

---

### Part 2: Deploy Frontend on Vercel

Vercel will build and distribute the React SPA globally.

1. **Sign in to Vercel:**
   Go to [vercel.com](https://vercel.com) and log in with GitHub.

2. **Import Project:**
   - Click **Add New…** → **Project**.
   - Find and click **Import** next to `codexshivam/careercompass`.

3. **Configure Project Settings:**
   - **Framework Preset:** `Vite` (auto-detected)
   - **Root Directory:** `./` (default root)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

4. **Add Environment Variable:**
   Expand the **Environment Variables** section and add:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** Your Railway backend URL (e.g., `https://careercompass-production-xxxx.up.railway.app`)  
     *(Do NOT add a trailing slash `/`)*

5. **Deploy:**
   - Click **Deploy**.
   - In ~30 seconds, Vercel will provide your live URL: `https://careercompass.vercel.app`.

---

## 3. Local Development

To run the project locally on your machine:

### 1. Start Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Backend runs at `http://127.0.0.1:8000`.

### 2. Start Frontend (in a second terminal):
```bash
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`. `src/api.ts` automatically defaults to `http://127.0.0.1:8000` when `VITE_API_BASE_URL` is not set locally.

---

## 4. REST API Endpoint Reference

All endpoints are hosted on your Railway backend:

| Method | Route | Input Format | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/predict/promotion` | `{"dashboard":4.0,"maths":4.0,"ai_ml":4.0,"big_data":3.5,"coding":4.2}` | Scores competency inputs against SAS model and returns probability, percentage, verdict, and dynamic +0.5 upskilling ROI recommendation |
| `GET` | `/api/meta/competencies` | None | Returns the 5 competency dimensions, scale labels, and default ratings |
| `GET` | `/api/salary/config` | None | Returns roles dropdown options and Seniority Premium comparison chart data |
| `POST` | `/api/salary/estimate` | `{"role":"DS","experience":3.0,"senior":false,"location":"metro"}` | Calculates compensation estimate with breakdown |
| `GET` | `/api/matrix` | None | Returns the 4 Skill Gap Matrix cards |
| `GET` | `/api/personas` | None | Returns the 4 Leadership Personas clusters |

---

## 5. Model Maintenance & Updates

The SAS scoring engine is located at `backend/sas_engine.py`.

If model parameters are updated in SAS Viya:
1. Open `backend/sas_engine.py`.
2. Update the equation inside `score_record()`:
   ```python
   z = (
       -26.2236
       + 1.8210 * maths
       + 1.3547 * dashboard
       + 1.2639 * ai_ml
       + 0.9961 * big_data
       + 0.6090 * coding
   )
   ```
3. Commit and push:
   ```bash
   git add backend/sas_engine.py
   git commit -m "update model weights"
   git push
   ```
4. Railway will automatically detect the push, rebuild, and redeploy your backend in under 1 minute.
