# ChittyOS Trust Engine - Deployment Guide

## 🚀 Deployment Architecture

```
chitty.cc/trust     ←→     trust.chitty.cc
   (Frontend)                  (API)
      ↓                         ↓
  trust_frontend.html     real_trust_api.py
      ↓                         ↓
  Static Website          Docker Container
                               ↓
                        PostgreSQL Database
```

## 📦 What's Ready for Deployment

### ✅ Backend API (trust.chitty.cc)
- **File**: `real_trust_api.py` - Real 6D trust calculation engine
- **Features**:
  - Real ChittyTrust algorithm (no fake data)
  - User creation and event tracking
  - ChittyID format support (`id.chitty.cc/ABC12345`)
  - Production CORS configuration
  - Health monitoring endpoints

### ✅ Frontend Interface (chitty.cc/trust)
- **File**: `templates/trust_frontend.html` - Complete trust interface
- **Features**:
  - Real-time trust score calculation
  - User and event management
  - 6D dimension visualization
  - ChittyID support
  - API status monitoring

### ✅ Production Configuration
- `requirements.txt` - Python dependencies
- `gunicorn.conf.py` - Production WSGI server config
- `Dockerfile` - Container deployment
- `.env.example` - Environment variables
- `deploy.sh` - Deployment automation script

## 🔧 Deployment Steps

### 1. Deploy API to trust.chitty.cc

```bash
# Build and deploy Docker container
docker build -t chittyos/trust-api .
docker run -d -p 8000:8000 \
  -e PRODUCTION=true \
  -e DATABASE_URL=postgresql://user:pass@db:5432/chitty_trust \
  chittyos/trust-api

# Or use gunicorn directly
PRODUCTION=true gunicorn --config gunicorn.conf.py real_trust_api:app
```

### 2. Deploy Frontend to chitty.cc/trust

```bash
# Upload frontend file to web server
scp templates/trust_frontend.html server:/var/www/chitty.cc/trust/index.html

# Configure web server (nginx example)
location /trust {
    try_files $uri $uri/ /trust/index.html;
}
```

### 3. Configure Environment

```bash
# Set environment variables
export PRODUCTION=true
export DATABASE_URL=postgresql://username:password@localhost:5432/chitty_trust
export PORT=8000

# Configure SSL certificates
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

## 🧪 Local Testing

### Start API Server (Port 5000)
```bash
python real_trust_api.py
```

### Start Frontend Server (Port 3000)
```bash
python frontend_server.py
```

### Test Complete Workflow
1. Visit: http://localhost:3000/trust
2. Create user: `alice`
3. Add events: verification, transaction
4. Calculate trust score

## 📊 API Endpoints

### Core Trust API
- `GET /api/trust/<entity_id>` - Calculate real trust score
- `POST /api/users/<user_id>` - Create user with credentials
- `POST /api/users/<user_id>/events` - Add trust events
- `GET /api/health` - API health and status

### Example Usage
```bash
# Create user
curl -X POST https://trust.chitty.cc/api/users/alice \
  -H "Content-Type: application/json" \
  -d '{"identity_verified":true,"credentials":["blockchain_verified"]}'

# Add event
curl -X POST https://trust.chitty.cc/api/users/alice/events \
  -H "Content-Type: application/json" \
  -d '{"type":"verification","outcome":"positive","description":"ID verified"}'

# Calculate trust
curl https://trust.chitty.cc/api/trust/alice
```

## 🔒 Security & Production Notes

- ✅ CORS configured for chitty.cc domains
- ✅ Production vs development modes
- ✅ Non-root Docker user
- ✅ Health checks included
- 🔧 SSL/TLS configuration ready
- 🔧 PostgreSQL database required for production
- 🔧 Environment variable security

## 🌐 Domain Configuration

### DNS Records Required
```
trust.chitty.cc    A    Your-API-Server-IP
chitty.cc         A    Your-Frontend-Server-IP
```

### SSL Certificates
- trust.chitty.cc - API SSL certificate
- chitty.cc - Frontend SSL certificate

## ✨ Real Features

- 🚫 **NO FAKE DATA** - Uses actual ChittyTrust 6D algorithm
- 🧮 **Real Calculations** - Source, Temporal, Channel, Outcome, Network, Justice Trust
- 🆔 **ChittyID Support** - Full `id.chitty.cc/ABC12345` format
- 📊 **6D Visualization** - Real-time dimension scoring
- 🔍 **Trust Explanations** - Detailed dimension analysis
- 💾 **Real Database** - User and event persistence
- 🔒 **Production Ready** - CORS, SSL, monitoring

## 🚀 Go Live!

Your ChittyOS Trust Engine is ready for production deployment with real 6D trust calculations!