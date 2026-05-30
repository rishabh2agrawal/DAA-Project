# ☁️ Deployment Guide

This guide details how to deploy the entire ClimateIQ dual-stack architecture to the cloud.

## 1. Cloud Architecture Strategy

The recommended stack utilizes **Render** or **Heroku** for hosting, as they natively support simultaneous API and UI deployments with Docker or pure Python environments.

*   **Backend:** Dedicated FastAPI webservice (Python Environment).
*   **Frontend:** Dedicated Streamlit UI (Python Environment).

## 2. Preparing for Production

**Ensure `requirements.txt` is updated.**
You can freeze modern requirements locally before deployment:
```bash
pip freeze > requirements.txt
```

**Modify Frontend Hardcoded IPs:**
In `frontend/app.py`, change:
```python
backend_url = "http://localhost:8000"
```
To point to your deployed backend URL:
```python
backend_url = os.getenv("BACKEND_URL", "https://your-backend.render.com")
```

## 3. Deploying to Render (Platform as a Service)

### Step 3a: Deploying the Backend
1. Connect your GitHub repository to Render.
2. Click **New +** > **Web Service**.
3. Select your repository.
4. **Environment:** `Python`
5. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Start Command:**
   ```bash
   uvicorn backend.app:app --host 0.0.0.0 --port $PORT
   ```
7. Click **Deploy**.

### Step 3b: Deploying the Frontend
1. Click **New +** > **Web Service**.
2. Select the *same* repository.
3. **Environment:** `Python`
4. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Start Command:**
   ```bash
   streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
   ```
6. **Set Environment Variable:**
   * `BACKEND_URL` = (The URL you copied from Step 3a).
7. Click **Deploy**.

## 4. Alternative: Deploying Streamlit via Streamlit Community Cloud
If you deploy the Backend to Render, you can deploy the UI totally free via **share.streamlit.io**.
1. Log in to Streamlit Share.
2. Deploy new app.
3. Main file path: `frontend/app.py`
4. Add the `BACKEND_URL` as a secret in the Advanced Settings configuration panel.