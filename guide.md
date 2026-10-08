# Career Compass — Full Production & Deployment Guide

> **Project:** Career Compass — Data Science Career Value Chain & Promotion Predictor  
> **Team:** Team Rocket (Chandigarh University)  
> **Stack:** React + TypeScript + Vite (Frontend) + FastAPI + Python (Backend & SAS Scoring Engine)

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT / BROWSER                     │
│               http://localhost:5173 (Dev)               │
│          https://your-frontend-domain.com (Prod)        │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP / JSON API
                             ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                       │
│               http://127.0.0.1:8000 (Dev)               │
│          https://your-backend-api.com (Prod)            │
├─────────────────────────────────────────────────────────┤
│ • /predict/promotion       • /api/salary/estimate       │
│ • /api/meta/competencies   • /api/matrix & /personas    │
├─────────────────────────────────────────────────────────┤
│              SAS MODEL SCORING ENGINE                   │
│               (backend/sas_engine.py)                   │
│   In-memory mathematical evaluation of SAS Viya model   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Local Development Setup

### Prerequisites
- **Node.js:** v18.0.0 or higher
- **Python:** v3.10, v3.11, v3.12, or v3.13
- **Git**

### Step 1: Clone Repository
```bash
git clone https://github.com/codexshivam/careercompass.git
cd careercompass
```

### Step 2: Run Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Backend will start on `http://127.0.0.1:8000`. Test it by visiting `http://127.0.0.1:8000/docs` for the interactive Swagger API documentation.

### Step 3: Run Frontend
Open a **new terminal tab**:
```bash
cd careercompass
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173`.

---

## 3. Production Deployment Options

---

### Option A: Render.com (Recommended for Free Full-Stack Deployment)

Render allows you to host both the FastAPI backend and React frontend with free SSL and automated GitHub CI/CD deployments.

#### 1. Deploy the Backend on Render
1. Go to [Render Dashboard](https://dashboard.render.com) and click **New +** → **Web Service**.
2. Connect your GitHub repo (`codexshivam/careercompass`).
3. Set the following configuration:
   - **Name:** `careercompass-api`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Click **Create Web Service**.
5. Once deployed, copy your backend URL (e.g., `https://careercompass-api.onrender.com`).

#### 2. Configure & Deploy Frontend on Render / Vercel
1. Update `src/api.ts` so `API_BASE` points to your deployed backend:
   ```typescript
   const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://careercompass-api.onrender.com'
   ```
2. Create a **Static Site** on Render:
   - **Root Directory:** leave blank (root of repo)
   - **Build Command:** `npm run build`
   - **Publish Directory:** `dist`
   - **Environment Variable:** `VITE_API_BASE_URL` = `https://careercompass-api.onrender.com`
3. Click **Create Static Site**.

---

### Option B: Vercel (Frontend) + Railway / Render (Backend)

#### 1. Deploy Frontend on Vercel
1. Go to [vercel.com](https://vercel.com) and import the repository.
2. Framework Preset: **Vite**.
3. Build Settings:
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Environment Variables:
   - `VITE_API_BASE_URL`: `https://your-backend-url.railway.app`
5. Click **Deploy**.

---

### Option C: Single Linux Server (Ubuntu VPS / AWS EC2 / DigitalOcean)

If deploying to a single Ubuntu 22.04 / 24.04 server:

#### 1. Server Prerequisites & Nginx Setup
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nodejs npm nginx git
```

#### 2. Clone and Setup Backend Systemd Service
```bash
cd /var/www
sudo git clone https://github.com/codexshivam/careercompass.git
cd careercompass/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create Systemd Service (`/etc/systemd/system/careercompass.service`):
```ini
[Unit]
Description=Career Compass FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/careercompass/backend
ExecStart=/var/www/careercompass/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the backend service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable careercompass
sudo systemctl start careercompass
```

#### 3. Build Frontend
```bash
cd /var/www/careercompass
npm install
npm run build
```

#### 4. Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/careercompass`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend Static Assets
    location / {
        root /var/www/careercompass/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Reverse Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /predict/ {
        proxy_pass http://127.0.0.1:8000/predict/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site & reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/careercompass /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 4. Docker & Containerized Deployment

You can also package the entire application using Docker.

### `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Run Container
```bash
cd backend
docker build -t careercompass-backend .
docker run -d -p 8000:8000 --name careercompass-api careercompass-backend
```

---

## 5. API Reference Summary

| Method | Route | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/predict/promotion` | `{"dashboard":4.0,"maths":4.0,"ai_ml":4.0,"big_data":3.5,"coding":4.2}` | Scores competency inputs against SAS model and outputs probability, verdict & Upskilling ROI |
| `GET` | `/api/meta/competencies` | None | Returns metadata for the 5 competency sliders |
| `GET` | `/api/salary/config` | None | Returns role options and seniority premium benchmark chart |
| `POST` | `/api/salary/estimate` | `{"role":"DS","experience":3.0,"senior":false,"location":"metro"}` | Calculates compensation estimate with breakdown |
| `GET` | `/api/matrix` | None | Returns the 4 Skill Gap Matrix dimensions |
| `GET` | `/api/personas` | None | Returns the 4 Leadership Personas clusters |

---

## 6. Maintenance & Model Retraining

If you update the model weights in SAS Viya:
1. Open `backend/sas_engine.py`.
2. Update the coefficient values in `score_record()`:
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
3. Commit and push to GitHub (`git commit -am "update model weights" && git push`). Your cloud hosting service will auto-deploy the updated model.
