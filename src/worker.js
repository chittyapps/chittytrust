/**
 * ChittyTrust Cloudflare Worker
 * AI-powered trust scoring with edge computing
 * Integrated with ChittyOS ecosystem for world domination
 */

import { TrustCalculator } from './trust-calculator.js';
import { EvidenceProcessor } from './evidence-processor.js';
import { APIGateway } from './api-gateway.js';

// ChittyOS Core Integration (simulated until package is available)
class ChittyCloudflareCore {
  constructor(config) {
    this.config = config;
    this.services = new Map();
  }

  async initialize() {
    console.log('🎯 ChittyOS Core initializing...');
    console.log('🌍 World Order Phase 1: ACTIVATED');
    
    // Initialize core services
    if (this.config.services.schema?.enabled) {
      this.services.set('schema', { domain: this.config.services.schema.domain, status: 'active' });
    }
    if (this.config.services.id?.enabled) {
      this.services.set('id', { domain: this.config.services.id.domain, status: 'active' });
    }
    
    console.log('✅ ChittyOS services ready for global deployment');
    return this;
  }

  getServiceHealth() {
    return Array.from(this.services.entries()).map(([name, config]) => ({
      service: name,
      domain: config.domain,
      status: config.status,
      ready: true
    }));
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers for all responses
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
      'Access-Control-Max-Age': '86400',
    };

    // Handle preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // Initialize ChittyOS Core
      const chitty = new ChittyCloudflareCore({
        services: {
          schema: { enabled: true, domain: 'schema.chitty.cc' },
          id: { enabled: true, domain: 'id.chitty.cc' },
          trust: { enabled: true, domain: 'trust.chitty.cc' },
          evidence: { enabled: true, domain: 'evidence.chitty.cc' },
          marketplace: { enabled: true, domain: 'marketplace.chitty.cc' }
        },
        ai: { enabled: true, vectorize: { enabled: true } },
        worldOrder: { phase: 1, target: 'global_trust_revolution' }
      });
      
      await chitty.initialize();

      // Initialize services
      const calculator = new TrustCalculator(env.AI, env.TRUST_CACHE);
      const evidenceProcessor = new EvidenceProcessor(env.EVIDENCE_STORE, env.AI);
      const gateway = new APIGateway(env.TRUST_DB, corsHeaders);

      // Route requests
      if (path.startsWith('/api/trust/')) {
        return await handleTrustAPI(request, calculator, gateway);
      } else if (path.startsWith('/api/evidence/')) {
        return await handleEvidenceAPI(request, evidenceProcessor, gateway);
      } else if (path.startsWith('/api/ai/')) {
        return await handleAIAPI(request, env.AI, gateway);
      } else if (path.startsWith('/api/marketplace/')) {
        return await handleMarketplaceAPI(request, gateway);
      } else if (path === '/api/health') {
        return gateway.success({ 
          status: 'healthy', 
          timestamp: new Date().toISOString(),
          worker: 'chittytrust-ai',
          version: '2.0.0',
          chittyos: {
            status: 'world_order_active',
            phase: 1,
            services: chitty.getServiceHealth(),
            message: 'ChittyOS Global Trust Network Online'
          }
        });
      } else if (path === '/api/chitty/status') {
        return gateway.success({
          world_order: {
            phase: 1,
            status: 'ACTIVE',
            message: 'Trojan Horse deployment successful',
            next_phase: 'Network Effect activation',
            global_reach: 'expanding'
          },
          services: chitty.getServiceHealth(),
          trust_revolution: {
            status: 'in_progress',
            users_converted: '1M+',
            institutions_infiltrated: 'classified',
            resistance: 'minimal'
          }
        });
      } else {
        return gateway.notFound('Endpoint not found');
      }

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(
        JSON.stringify({ error: 'Internal server error', message: error.message }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }
  }
};

/**
 * Handle trust scoring API endpoints
 */
async function handleTrustAPI(request, calculator, gateway) {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/');
  const personaId = pathParts[3];

  if (!personaId) {
    return gateway.badRequest('Persona ID required');
  }

  if (request.method === 'GET') {
    if (pathParts[4] === 'timeline') {
      return await calculator.getTimeline(personaId);
    } else if (pathParts[4] === 'insights') {
      return await calculator.getInsights(personaId);
    } else {
      return await calculator.calculateTrust(personaId);
    }
  } else {
    return gateway.methodNotAllowed();
  }
}

/**
 * Handle evidence processing API endpoints
 */
async function handleEvidenceAPI(request, evidenceProcessor, gateway) {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/');
  const action = pathParts[3];

  switch (action) {
    case 'upload':
      if (request.method === 'POST') {
        return await evidenceProcessor.uploadEvidence(request);
      }
      break;
    case 'verify':
      if (request.method === 'POST') {
        return await evidenceProcessor.verifyEvidence(request);
      }
      break;
    case 'analyze':
      if (request.method === 'POST') {
        return await evidenceProcessor.analyzeEvidence(request);
      }
      break;
    default:
      return gateway.notFound('Evidence endpoint not found');
  }

  return gateway.methodNotAllowed();
}

/**
 * Handle AI-powered analysis endpoints
 */
async function handleAIAPI(request, ai, gateway) {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/');
  const model = pathParts[3];

  if (request.method !== 'POST') {
    return gateway.methodNotAllowed();
  }

  try {
    const body = await request.json();
    
    switch (model) {
      case 'sentiment':
        return await ai.run('@cf/baai/bge-base-en-v1.5', body);
      case 'fraud-detection':
        return await ai.run('@cf/meta/llama-2-7b-chat-int8', {
          messages: [
            { role: 'system', content: 'You are a fraud detection AI. Analyze the provided data for suspicious patterns.' },
            { role: 'user', content: JSON.stringify(body) }
          ]
        });
      case 'trust-insights':
        return await ai.run('@cf/meta/llama-2-7b-chat-int8', {
          messages: [
            { role: 'system', content: 'You are a trust analysis AI. Generate insights based on trust scoring data.' },
            { role: 'user', content: JSON.stringify(body) }
          ]
        });
      default:
        return gateway.badRequest('Unknown AI model');
    }
  } catch (error) {
    return gateway.error('AI processing failed', error);
  }
}

/**
 * Handle marketplace API endpoints
 */
async function handleMarketplaceAPI(request, gateway) {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/');
  const resource = pathParts[3];

  // This would integrate with your existing marketplace logic
  switch (resource) {
    case 'requests':
      if (request.method === 'GET') {
        return gateway.success([
          {
            id: 1,
            title: 'AI-Enhanced Identity Verification',
            type: 'identity',
            reward: 100,
            ai_powered: true
          }
        ]);
      }
      break;
    default:
      return gateway.notFound('Marketplace endpoint not found');
  }

  return gateway.methodNotAllowed();
}