# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **🎯 Project Orchestration:** This project follows [ChittyCan™ Project Standards](../CHITTYCAN_PROJECT_ORCHESTRATOR.md)

## Repository Structure

This is a **multi-project monorepo** containing several ChittyOS services. The root directory hosts the **ChittyScore 6D Trust Scoring Engine** (Python/Flask). Sub-projects are independent applications:

- **chittyscore/** (root) - Python Flask behavioral trust scoring engine
- **chittyfinance/** - Financial tracking service (TypeScript/Node)
- **chittyverify/** - Evidence verification service (TypeScript/Node)
- **chittypm/** - Project management and orchestration tools
- **chitty-frontend/** - React/Vite frontend application

Each sub-project has its own package.json, dependencies, and may have its own CLAUDE.md file for specific guidance.

## Development Commands

### ChittyScore Engine (Root Project)

**Running locally:**
```bash
python main.py                                             # Development server on port 5000
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app  # Development with auto-reload
gunicorn --bind 0.0.0.0:5000 main:app                      # Production mode
```

**Database setup:**
```bash
# Initialize D1 database (Cloudflare) with schema
psql $DATABASE_URL < schema.sql

# Schema includes: trust_scores, evidence_records, verification_requests,
# trust_events, ai_insights, api_usage tables
```

**Deployment:**
```bash
# Cloudflare Workers deployment
npm run deploy              # Deploy to Cloudflare (uses wrangler.toml)

# Docker deployment
docker build -t chittyscore-api .
docker run -p 8000:8000 -e DATABASE_URL=$DATABASE_URL chittyscore-api
```

**Note:** The repository references `app.py` in `main.py`, but this file may be missing or needs to be created. The trust scoring engine core is in `src/chitty_score/`.

### Sub-Projects

Navigate to each sub-project directory and use standard Node.js commands:
```bash
cd chittyfinance/    # or chittyverify/
npm install
npm run dev         # Development server
npm run build       # Production build
npm test            # Run tests
```

## Core Architecture

### ChittyScore 6D Trust Scoring Engine

A sophisticated behavioral trust scoring system with **6 dimensions** that produces **4 output scores**:

**Trust Dimensions (Input):**
- **Source** (15% weight) - Identity verification and credentials (src/chitty_score/dimensions.py:24)
- **Temporal** (10% weight) - Historical consistency and longevity
- **Channel** (15% weight) - Communication channel reliability
- **Outcome** (20% weight) - Track record of positive outcomes
- **Network** (15% weight) - Quality of network connections
- **Justice** (25% weight) - Alignment with justice principles

**Output Scores:**
- **People Score** - Interpersonal trust assessment
- **Legal Score** - Legal system alignment
- **State Score** - Institutional trust level
- **ChittyScore** - Overall ChittyOS trust rating

**Trust Level Mapping:**
Composite scores map to ChittyID lifecycle levels:
- L4 (90+): Institutional
- L3 (75+): Professional
- L2 (50+): Enhanced
- L1 (25+): Basic
- L0 (0+): Anonymous

### Python Module Structure

**Trust Scoring Engine Core (`src/chitty_score/`):**
- `dimensions.py` - 6 dimension calculation classes (SourceDimension, TemporalDimension, etc.)
- `models.py` - Pydantic data models (TrustEntity, TrustEvent, Credential, Connection)
- `analytics.py` - Trust insights generation and pattern detection

**Additional Python Packages (`packages/chitty-score/`):**
- Mirror of core trust scoring modules (may be for packaging/distribution)

### Database Schema

**Primary Tables (schema.sql):**
- `trust_scores` - Historical trust score records with all 6 dimensions + 4 output scores
- `evidence_records` - Blockchain-verified evidence with chain of custody
- `verification_requests` - Marketplace verification requests with rewards
- `trust_events` - Timeline of trust-affecting events
- `ai_insights` - AI-generated insights and recommendations
- `api_usage` - API usage tracking and analytics

**Database Configuration:**
- PostgreSQL via `DATABASE_URL` environment variable
- Cloudflare D1 for Workers deployment
- Sample demo personas: `alice`, `bob`, `charlie` (see schema.sql:118-125)

### Deployment Architecture

**Hybrid Deployment Strategy:**
1. **Cloudflare Workers** - Edge deployment for API (wrangler.toml)
   - Bindings: AI, KV (TRUST_CACHE), D1 (TRUST_DB), R2 (EVIDENCE_STORE)
   - Environments: staging, production

2. **Flask/Gunicorn** - Traditional server deployment (Dockerfile, .replit)
   - Used for Replit hosting
   - Can run standalone with PostgreSQL

3. **Frontend** - Static assets served via templates/ (Jinja2) or chitty-frontend/ (React)

## Key Development Patterns

### Async Trust Calculations

All trust calculations use async/await. Flask routes handle this with event loop pattern:
```python
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(calculate_trust(entity, events))
loop.close()
```

### Missing Files

The codebase references several files that don't exist in the repository:
- `app.py` - Flask application (imported by main.py but missing)
- `auth.py` - Authentication system
- `marketplace.py` - Marketplace service logic
- `real_trust_api.py` - API entry point (referenced in Dockerfile)
- `gunicorn.conf.py` - Gunicorn configuration

If working with Flask routes, these may need to be created or the references updated.

### Data Models

**TrustEntity** (src/chitty_score/models.py:63):
- Pydantic model for entities being scored
- Fields: id, entity_type, name, credentials, connections, transparency_level

**TrustEvent** (src/chitty_score/models.py:76):
- Events that affect trust scores
- Types: transaction, verification, endorsement, dispute, collaboration, review, achievement
- Outcomes: positive, negative, neutral, pending

### Environment Variables

Required for deployment (.env.example):
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default 8000 for production, 5000 for dev)
- `PRODUCTION` - Production mode flag
- `ALLOWED_ORIGINS` - CORS domains (comma-separated)
- `SENTRY_DSN` - Optional error tracking
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

## Working with Sub-Projects

Each sub-project is a standalone application. Before working on one:

1. **Read its CLAUDE.md** (if present) - e.g., chittyverify/CLAUDE.md
2. **Check its package.json** for available scripts
3. **Install dependencies** - `npm install` or `npm ci`
4. **Understand its purpose** within the ChittyOS ecosystem

Sub-projects may have different tech stacks, databases, and deployment strategies than the root project.