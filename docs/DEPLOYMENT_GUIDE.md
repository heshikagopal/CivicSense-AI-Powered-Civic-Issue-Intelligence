# CivicSense Deployment Guide

This guide details how to deploy **CivicSense – AI-Powered Civic Issue Intelligence** to the cloud.

Because the FastAPI backend automatically serves the compiled React single-page application (`frontend/dist/`), you can deploy the entire full-stack platform as **a single web service** or decouple it into frontend and backend tiers.

---

## Method 1: Render.com (Recommended – Free & Easiest)

Render can build and run both the Python AI backend and the React frontend in a single free service directly from your GitHub repository.

### Step-by-Step Instructions:
1. Go to **[https://render.com/](https://render.com/)** and sign in with your GitHub account.
2. Click **"New +"** in the top navigation and select **"Web Service"**.
3. Select **"Build and deploy from a Git repository"** and connect:
   `https://github.com/heshikagopal/CivicSense-AI-Powered-Civic-Issue-Intelligence`
4. Configure the service settings:
   - **Name:** `civicsense`
   - **Region:** Oregon (US West) or nearest to you
   - **Runtime:** `Python 3`
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
     ```
   - **Start Command:**
     ```bash
     python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free`
5. In **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.12.7`
   - `SECRET_KEY`: *(Any random 32-character string or click generate)*
   - `DATABASE_URL`: `sqlite:///./civicsense.db`
6. Click **"Create Web Service"**.
7. Render will build the React bundle, install the AI models, and give you a public URL (e.g., `https://civicsense.onrender.com`).

---

## Method 2: Railway.app (Instant 1-Click Cloud Deploy)

Railway provides high-memory containers ideal for PyTorch and computer vision workloads.

1. Go to **[https://railway.app/](https://railway.app/)** and sign in with GitHub.
2. Click **"New Project"** -> **"Deploy from GitHub repo"**.
3. Select `heshikagopal/CivicSense-AI-Powered-Civic-Issue-Intelligence`.
4. Under **Settings** -> **Build**:
   - **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..`
   - **Start Command:** `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Variables**, add:
   - `SECRET_KEY`: `civicsense-production-secret-2026`
6. Railway will automatically deploy and generate a public HTTPS domain.

---

## Method 3: Self-Hosted Docker Compose (AWS EC2 / DigitalOcean Droplet / Ubuntu Server)

For production deployments requiring PostgreSQL 16 + PostGIS + pgvector:

### 1. Provision a Linux Server
Launch an Ubuntu 22.04 / 24.04 VPS (minimum 2 vCPUs, 4GB RAM).

### 2. Install Docker & Git
```bash
sudo apt update && sudo apt install -y docker.io docker-compose git
sudo systemctl enable --now docker
```

### 3. Clone Repository
```bash
git clone https://github.com/heshikagopal/CivicSense-AI-Powered-Civic-Issue-Intelligence.git
cd CivicSense-AI-Powered-Civic-Issue-Intelligence
```

### 4. Build Frontend & Launch Containers
```bash
# Build frontend
cd frontend && npm install && npm run build && cd ..

# Launch backend + PostGIS + pgvector
docker-compose up -d --build
```

### 5. Access
Open `http://YOUR_SERVER_IP:8000/`.

---

## Method 4: Decoupled (Vercel Frontend + Render/Fly.io Backend)

If you prefer hosting the React client separately on Vercel or Netlify:

### Backend:
1. Deploy `backend/` to Render or Fly.io using:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
2. Copy your backend URL (e.g. `https://civicsense-api.onrender.com`).

### Frontend:
1. Import the repository on **Vercel** ([https://vercel.com/](https://vercel.com/)).
2. Set **Root Directory** to `frontend`.
3. Set **Framework Preset** to `Vite`.
4. Add environment variable:
   - `VITE_API_URL`: `https://civicsense-api.onrender.com`
5. Deploy.

---

## Verifying Deployment

Once deployed, verify:
1. Health endpoint returns 200: `https://your-domain.com/health`
2. Swagger API docs are accessible: `https://your-domain.com/docs`
3. Frontend single-page app loads with live database statistics: `https://your-domain.com/`
4. Log in with the pre-seeded credentials:
   - **Admin:** `admin@civicsense.org` / `Admin123!`
   - **Officer:** `officer@civicsense.org` / `Officer123!`
   - **Citizen:** `citizen@civicsense.org` / `Citizen123!`
