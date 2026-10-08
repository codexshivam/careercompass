# Career Compass — Technical Architecture & Guide

This document outlines the architecture, local SAS scoring engine, and setup for Career Compass.

---

## 1. Overview & Architecture

Career Compass runs on a **FastAPI backend** connected to a **React + TypeScript frontend**:
- **Frontend (`src/`):** Clean, reactive UI with debounced slider controls, salary calculators, and matrix views.
- **Backend (`backend/`):** Direct Python execution of the SAS model scoring rules (`backend/sas_engine.py`) derived from SAS Viya Model Studio (`dmcas_epscorecode.sas`).
- **No external API dependencies or token expirations:** The model scores locally in memory in `< 5ms`.

---

## 2. Running the Application

### Step 1: Start the Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Backend will start on `http://127.0.0.1:8000`.

### Step 2: Start the Frontend (React + Vite)
In another terminal window:
```bash
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

---

## 3. Backend Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/predict/promotion` | Executes the SAS model scoring rules and computes Upskilling ROI |
| `GET` | `/api/meta/competencies` | Returns competency dimensions, defaults, and scale labels |
| `GET` | `/api/salary/config` | Returns target roles and seniority premium chart data |
| `POST` | `/api/salary/estimate` | Computes compensation based on role, experience, seniority, and location |
| `GET` | `/api/matrix` | Returns market demand vs. promotion reward matrix cards |
| `GET` | `/api/personas` | Returns leadership personas and success win rates |

---

## 4. SAS Scoring Engine Details (`backend/sas_engine.py`)

The promotion hike model uses the logistic link function directly derived from your SAS Model Studio / SAS Viya scoring code:

```python
z = (
    -26.2236
    + 1.8210 * maths
    + 1.3547 * dashboard
    + 1.2639 * ai_ml
    + 0.9961 * big_data
    + 0.6090 * coding
)
probability = 1.0 / (1.0 + exp(-z))
```

### Upskilling ROI Algorithm:
For each competency score $< 5.0$, the engine calculates hypothetical probabilities with a $+0.5$ boost and returns the competency with the highest delta in real time.
