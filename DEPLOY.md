# ChittyScore Deployment Guide

## Free Hosting Options

This guide covers **100% free** deployment options for the ChittyScore API.

---

## Option 1: Replit (Easiest - Already Configured ✅)

**Why:** Your `.replit` file is already configured. Just import and run!

### Steps:

1. **Go to** [replit.com](https://replit.com)
2. **Click** "Create Repl" → "Import from GitHub"
3. **Enter repo URL** or upload this folder
4. **Click "Run"** - That's it!

**URL:** Your app will be at `https://<your-repl-name>.repl.co`

**Pros:**
- Zero configuration needed
- Free PostgreSQL database included
- Auto-deploys on code changes
- Built-in IDE

**Cons:**
- Repl goes to sleep after inactivity (free tier)
- Public by default

---

## Option 2: Fly.io (Best Free Tier)

**Why:** 3 free VMs + 3GB storage, no credit card needed initially.

### Prerequisites:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth signup  # or flyctl auth login
```

### Deploy:

1. **Initialize Fly.io app:**
```bash
cd /Users/nb/projects/development/chittyscore
flyctl launch
```

2. **Follow prompts:**
   - App name: `chittyscore-api` (or your choice)
   - Region: Choose closest to you
   - PostgreSQL: No (or Yes if you need database)
   - Deploy now: Yes

3. **Set environment variables (optional):**
```bash
flyctl secrets set DATABASE_URL="your_postgres_url_here"
flyctl secrets set PORT=8000
```

4. **Deploy updates:**
```bash
flyctl deploy
```

**URL:** `https://chittyscore-api.fly.dev`

**Pros:**
- Always on (doesn't sleep)
- Fast global CDN
- Simple CLI
- PostgreSQL included in free tier

**Cons:**
- Requires credit card after trial (but won't charge on free tier)

---

## Option 3: Render (Easiest Auto-Deploy)

**Why:** Auto-deploys from GitHub, includes free PostgreSQL.

### Steps:

1. **Go to** [render.com](https://render.com)
2. **Sign up** with GitHub
3. **Click** "New +" → "Web Service"
4. **Connect** your GitHub repo
5. **Configure:**
   - Name: `chittyscore-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - Instance Type: `Free`

6. **Add Environment Variables:**
   - `PYTHON_VERSION` = `3.11.0`
   - `DATABASE_URL` = (get from Render PostgreSQL service)

7. **Click** "Create Web Service"

**URL:** `https://chittyscore-api.onrender.com`

**Pros:**
- Auto-deploys from GitHub
- Free PostgreSQL database
- SSL certificate included
- Zero config after setup

**Cons:**
- Free tier spins down after 15 min inactivity (cold start ~30 sec)

---

## Option 4: Railway (Generous Free Tier)

**Why:** $5 free credit per month, PostgreSQL included.

### Steps:

1. **Go to** [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click** "New Project" → "Deploy from GitHub repo"
4. **Select** your chittyscore repo
5. **Railway auto-detects** Python and Dockerfile
6. **Add PostgreSQL:**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway auto-injects `DATABASE_URL`

7. **Deploy!**

**URL:** Railway provides a public URL like `https://chittyscore-production.up.railway.app`

**Pros:**
- PostgreSQL included
- No cold starts
- Simple dashboard
- $5/month free credit

**Cons:**
- Free credit runs out after ~500 hours/month
- Requires credit card verification

---

## Testing Your Deployment

Once deployed, test your API:

### Health Check:
```bash
curl https://your-app-url.com/api/health
```

### Demo Persona Test:
```bash
curl https://your-app-url.com/api/trust/demo/alice
```

### Calculate Custom Trust Score:
```bash
curl -X POST https://your-app-url.com/api/trust/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "entity": {
      "id": "test_user_1",
      "entity_type": "person",
      "name": "Test User",
      "created_at": "2024-01-01T00:00:00",
      "identity_verified": true,
      "credentials": [],
      "connections": [],
      "transparency_level": 0.8
    },
    "events": [
      {
        "id": "evt1",
        "entity_id": "test_user_1",
        "event_type": "verification",
        "timestamp": "2024-06-01T00:00:00",
        "channel": "verified_api",
        "outcome": "positive",
        "impact_score": 5.0
      }
    ]
  }'
```

---

## Recommended Free Tier Comparison

| Platform | Setup Time | Always On? | Database | Auto-Deploy | Best For |
|----------|-----------|-----------|----------|-------------|----------|
| **Replit** | 2 min | No (sleeps) | ✅ Included | ✅ Auto | Quick testing |
| **Fly.io** | 5 min | ✅ Yes | ✅ Included | Manual | Production-ready |
| **Render** | 5 min | No (sleeps) | ✅ Included | ✅ Auto | GitHub workflows |
| **Railway** | 5 min | ✅ Yes | ✅ Included | ✅ Auto | Best DX |

---

## My Recommendation

**For quick testing:** Use **Replit** (2 minutes, already configured)

**For production:** Use **Fly.io** (doesn't sleep, fast, generous free tier)

**For GitHub auto-deploy:** Use **Render** (free PostgreSQL, auto-deploys)

---

## Local Development

To run locally:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
python main.py
```

App runs at `http://localhost:5000`

Test endpoints:
- Health: http://localhost:5000/api/health
- Alice demo: http://localhost:5000/api/trust/demo/alice
- Bob demo: http://localhost:5000/api/trust/demo/bob
- Charlie demo: http://localhost:5000/api/trust/demo/charlie
