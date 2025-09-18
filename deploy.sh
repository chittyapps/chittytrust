#!/bin/bash

# Deployment script for ChittyOS Trust Engine
# Deploy API to trust.chitty.cc and frontend to chitty.cc/trust

echo "🚀 ChittyOS Trust Engine Deployment Script"
echo "==========================================="

# Configuration
API_DOMAIN="trust.chitty.cc"
FRONTEND_DOMAIN="chitty.cc"
DOCKER_IMAGE="chittyos/trust-api"

echo "📦 Building Docker image..."
docker build -t $DOCKER_IMAGE .

echo "🔧 Setting up environment variables..."
export PRODUCTION=true
export PORT=8000
export DATABASE_URL=${DATABASE_URL:-"postgresql://user:pass@localhost:5432/chitty_trust"}

echo "🌐 Deploying API to $API_DOMAIN..."
# This would typically involve:
# - Pushing Docker image to registry
# - Updating Kubernetes/Docker Compose
# - Setting up SSL certificates
# - Configuring reverse proxy

echo "📱 Deploying frontend to $FRONTEND_DOMAIN/trust..."
# This would typically involve:
# - Building static assets
# - Uploading to CDN/web server
# - Configuring routing

echo "✅ Deployment configuration ready!"
echo ""
echo "Manual steps required:"
echo "1. Deploy Docker image to $API_DOMAIN server"
echo "2. Upload trust_frontend.html to $FRONTEND_DOMAIN/trust/"
echo "3. Configure DNS and SSL certificates"
echo "4. Set up PostgreSQL database"
echo "5. Configure environment variables"
echo ""
echo "API Health Check: https://$API_DOMAIN/api/health"
echo "Frontend URL: https://$FRONTEND_DOMAIN/trust/"
echo ""
echo "🔥 Real trust calculations ready for production!"