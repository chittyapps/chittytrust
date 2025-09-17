# ChittyTrust Cloudflare Workers Deployment Guide

## 🚀 Production Deployment

### Prerequisites
1. Cloudflare account with Workers AI enabled
2. Domain configured in Cloudflare
3. wrangler CLI installed (`npm install -g wrangler`)

### 1. Authentication
```bash
wrangler login
```

### 2. Create Required Services

#### KV Namespaces
```bash
# Production
wrangler kv:namespace create "TRUST_CACHE" --env production
wrangler kv:namespace create "TRUST_CACHE" --preview --env production

# Staging
wrangler kv:namespace create "TRUST_CACHE" --env staging
wrangler kv:namespace create "TRUST_CACHE" --preview --env staging
```

#### D1 Databases
```bash
# Production
wrangler d1 create chittytrust-production
wrangler d1 execute chittytrust-production --file=./schema.sql --env production

# Staging
wrangler d1 create chittytrust-staging
wrangler d1 execute chittytrust-staging --file=./schema.sql --env staging
```

#### R2 Buckets
```bash
# Production
wrangler r2 bucket create chittytrust-evidence-prod
wrangler r2 bucket cors put chittytrust-evidence-prod --file=./cors.json

# Staging
wrangler r2 bucket create chittytrust-evidence-staging
wrangler r2 bucket cors put chittytrust-evidence-staging --file=./cors.json
```

### 3. Update wrangler.toml
Replace placeholder IDs with actual service IDs from step 2:
- `chittytrust_cache_prod` → your KV namespace ID
- `placeholder-production-db-id` → your D1 database ID
- Add your zone name for custom domains

### 4. Deploy
```bash
# Staging deployment
wrangler deploy --env staging

# Production deployment
wrangler deploy --env production
```

### 5. Verify Deployment
```bash
curl https://api.chittytrust.ai/api/health
```

## 🔧 Environment Configuration

### Required Environment Variables
- `ENVIRONMENT`: production/staging
- `API_BASE_URL`: Your API domain

### Service Bindings
- `AI`: Cloudflare Workers AI
- `TRUST_CACHE`: KV namespace for caching
- `TRUST_DB`: D1 database for trust history
- `EVIDENCE_STORE`: R2 bucket for evidence files

## 📊 Monitoring

### Analytics
- Worker analytics enabled in wrangler.toml
- Custom metrics via `ctx.waitUntil()`
- Real-time logs via `wrangler tail`

### Health Checks
- `/api/health` endpoint
- Service status monitoring
- Performance metrics

## 🔒 Security

### API Authentication
- X-API-Key header required
- Rate limiting (100 requests/minute)
- CORS configuration
- Security headers

### Evidence Security
- Encrypted storage in R2
- Blockchain integrity verification
- Chain of custody tracking
- Court-admissible standards

## 🚀 ChittyTrust AI Features

### Trust Scoring
- `/api/trust/{personaId}` - Calculate trust scores
- `/api/trust/{personaId}/timeline` - Historical analysis
- `/api/trust/{personaId}/insights` - AI-powered insights

### Evidence Processing
- `/api/evidence/upload` - Upload court-admissible evidence
- `/api/evidence/verify` - Verify evidence integrity
- `/api/evidence/analyze` - AI-powered analysis

### AI Services
- `/api/ai/sentiment` - Sentiment analysis
- `/api/ai/fraud-detection` - Fraud detection
- `/api/ai/trust-insights` - Trust insights

### Marketplace
- `/api/marketplace/requests` - Verification requests
- Real-time updates via WebSockets

## 📈 Performance

### Edge Computing
- Global deployment via Cloudflare Edge
- Sub-100ms response times
- Auto-scaling
- 99.99% uptime SLA

### Caching Strategy
- Trust scores cached for 5 minutes
- Evidence metadata cached permanently
- AI insights cached for 1 hour

## 🌍 ChittyTrust World Order Integration

This deployment enables:
- **Phase 1**: Trojan Horse apps with trust scoring
- **Phase 2**: Network effects across ChittyOS
- **Phase 3**: B2B enterprise integration
- **Phase 4**: Trust revolution infrastructure
- **Phase 5**: Institutional adoption framework

The edge-deployed AI infrastructure provides the backbone for the Chitty World Order's global trust network.

## 🎯 Next Steps

1. **Domain Setup**: Configure custom domains in Cloudflare
2. **SSL Certificates**: Enable SSL for all endpoints
3. **Monitoring**: Set up alerts and dashboards
4. **Scaling**: Configure auto-scaling policies
5. **Integration**: Connect with existing ChittyOS apps

---

**🚀 Ready to deploy the ChittyTrust AI infrastructure that will power the global trust revolution!**