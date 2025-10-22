/**
 * API Gateway for ChittyTrust Cloudflare Workers
 * Handles routing, authentication, rate limiting, and response formatting
 */

export class APIGateway {
  constructor(database, corsHeaders) {
    this.db = database;
    this.corsHeaders = corsHeaders;
    this.rateLimits = new Map();
  }

  /**
   * Unified success response
   */
  success(data, status = 200) {
    return new Response(JSON.stringify({
      success: true,
      data,
      timestamp: new Date().toISOString(),
      worker: 'chittytrust-ai'
    }), {
      status,
      headers: {
        ...this.corsHeaders,
        'Content-Type': 'application/json',
        'X-Powered-By': 'ChittyTrust Workers AI'
      }
    });
  }

  /**
   * Unified error response
   */
  error(message, details = null, status = 500) {
    return new Response(JSON.stringify({
      success: false,
      error: message,
      details,
      timestamp: new Date().toISOString(),
      worker: 'chittytrust-ai'
    }), {
      status,
      headers: {
        ...this.corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Bad request response
   */
  badRequest(message, details = null) {
    return this.error(message, details, 400);
  }

  /**
   * Not found response
   */
  notFound(message = 'Resource not found') {
    return this.error(message, null, 404);
  }

  /**
   * Method not allowed response
   */
  methodNotAllowed(message = 'Method not allowed') {
    return this.error(message, null, 405);
  }

  /**
   * Rate limiting check
   */
  async checkRateLimit(request, limit = 100, window = 60000) {
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
    const key = `rate_limit:${clientIP}`;
    const now = Date.now();
    
    const existing = this.rateLimits.get(key);
    if (existing) {
      if (now - existing.resetTime < window) {
        if (existing.count >= limit) {
          return this.error('Rate limit exceeded', {
            limit,
            window: window / 1000,
            resetTime: existing.resetTime + window
          }, 429);
        }
        existing.count++;
      } else {
        // Reset window
        this.rateLimits.set(key, { count: 1, resetTime: now });
      }
    } else {
      this.rateLimits.set(key, { count: 1, resetTime: now });
    }

    return null; // No rate limit hit
  }

  /**
   * API key authentication
   */
  async authenticate(request) {
    const apiKey = request.headers.get('X-API-Key');
    
    if (!apiKey) {
      return this.error('API key required', null, 401);
    }

    // Validate API key (implement your validation logic)
    if (!this.isValidApiKey(apiKey)) {
      return this.error('Invalid API key', null, 403);
    }

    return null; // Authentication successful
  }

  /**
   * Request validation middleware
   */
  async validateRequest(request, schema = null) {
    // Content-Type validation for POST/PUT requests
    if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
      const contentType = request.headers.get('Content-Type');
      if (!contentType || !contentType.includes('application/json')) {
        return this.badRequest('Content-Type must be application/json');
      }
    }

    // Schema validation if provided
    if (schema && ['POST', 'PUT', 'PATCH'].includes(request.method)) {
      try {
        const body = await request.json();
        const validation = this.validateSchema(body, schema);
        if (!validation.valid) {
          return this.badRequest('Request validation failed', validation.errors);
        }
      } catch (error) {
        return this.badRequest('Invalid JSON in request body');
      }
    }

    return null; // Validation successful
  }

  /**
   * Schema validation helper
   */
  validateSchema(data, schema) {
    const errors = [];

    for (const [field, rules] of Object.entries(schema)) {
      const value = data[field];

      // Required field check
      if (rules.required && (value === undefined || value === null)) {
        errors.push(`Field '${field}' is required`);
        continue;
      }

      // Type check
      if (value !== undefined && rules.type && typeof value !== rules.type) {
        errors.push(`Field '${field}' must be of type ${rules.type}`);
      }

      // Min/Max length for strings
      if (rules.minLength && typeof value === 'string' && value.length < rules.minLength) {
        errors.push(`Field '${field}' must be at least ${rules.minLength} characters`);
      }

      if (rules.maxLength && typeof value === 'string' && value.length > rules.maxLength) {
        errors.push(`Field '${field}' must be no more than ${rules.maxLength} characters`);
      }

      // Pattern validation
      if (rules.pattern && typeof value === 'string' && !rules.pattern.test(value)) {
        errors.push(`Field '${field}' format is invalid`);
      }

      // Enum validation
      if (rules.enum && !rules.enum.includes(value)) {
        errors.push(`Field '${field}' must be one of: ${rules.enum.join(', ')}`);
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Logging middleware
   */
  async logRequest(request, response, startTime) {
    const duration = Date.now() - startTime;
    const logData = {
      timestamp: new Date().toISOString(),
      method: request.method,
      url: request.url,
      status: response.status,
      duration: `${duration}ms`,
      userAgent: request.headers.get('User-Agent'),
      clientIP: request.headers.get('CF-Connecting-IP'),
      country: request.headers.get('CF-IPCountry'),
      ray: request.headers.get('CF-RAY')
    };

    console.log('API Request:', JSON.stringify(logData));
  }

  /**
   * Database query helper with error handling
   */
  async query(sql, params = []) {
    try {
      if (!this.db) {
        throw new Error('Database not configured');
      }

      const result = await this.db.prepare(sql).bind(...params).all();
      return { success: true, data: result.results || [] };
    } catch (error) {
      console.error('Database query error:', error);
      return { 
        success: false, 
        error: error.message,
        sql: sql.substring(0, 100) + '...'
      };
    }
  }

  /**
   * Paginated query helper
   */
  async paginatedQuery(sql, params = [], page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const countSql = sql.replace(/SELECT .+ FROM/, 'SELECT COUNT(*) as total FROM').split(' ORDER BY')[0];
    
    const [countResult, dataResult] = await Promise.all([
      this.query(countSql, params),
      this.query(`${sql} LIMIT ${limit} OFFSET ${offset}`, params)
    ]);

    if (!countResult.success || !dataResult.success) {
      throw new Error('Pagination query failed');
    }

    const total = countResult.data[0]?.total || 0;
    const totalPages = Math.ceil(total / limit);

    return {
      data: dataResult.data,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    };
  }

  /**
   * Cache response helper
   */
  cacheResponse(response, ttl = 300) {
    const headers = new Headers(response.headers);
    headers.set('Cache-Control', `public, max-age=${ttl}`);
    headers.set('X-Cache-TTL', ttl.toString());
    
    return new Response(response.body, {
      status: response.status,
      headers
    });
  }

  /**
   * Security headers helper
   */
  addSecurityHeaders(response) {
    const headers = new Headers(response.headers);
    
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('X-Frame-Options', 'DENY');
    headers.set('X-XSS-Protection', '1; mode=block');
    headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    headers.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'");
    
    return new Response(response.body, {
      status: response.status,
      headers
    });
  }

  /**
   * API key validation (implement your logic)
   */
  isValidApiKey(apiKey) {
    // Implement your API key validation logic
    // This could check against a database, KV store, or hardcoded values
    const validKeys = [
      'chitty_trust_api_key_001',
      'dev_key_12345',
      'prod_key_abcdef'
    ];
    
    return validKeys.includes(apiKey);
  }

  /**
   * Generate API response metadata
   */
  generateMetadata(data) {
    return {
      timestamp: new Date().toISOString(),
      version: '2.0.0',
      worker: 'chittytrust-ai',
      dataSize: JSON.stringify(data).length,
      responseId: this.generateResponseId()
    };
  }

  /**
   * Generate unique response ID
   */
  generateResponseId() {
    return 'resp_' + Math.random().toString(36).substring(2, 15);
  }

  /**
   * Handle WebSocket upgrades (if needed)
   */
  handleWebSocketUpgrade(request) {
    const upgradeHeader = request.headers.get('Upgrade');
    if (upgradeHeader !== 'websocket') {
      return this.badRequest('Expected WebSocket upgrade');
    }

    // WebSocket handling logic would go here
    return new Response('WebSocket upgrade not implemented', { status: 501 });
  }

  /**
   * Health check endpoint
   */
  healthCheck() {
    return this.success({
      status: 'healthy',
      uptime: process.uptime ? process.uptime() : 'unknown',
      memory: process.memoryUsage ? process.memoryUsage() : 'unknown',
      timestamp: new Date().toISOString(),
      worker: 'chittytrust-ai',
      version: '2.0.0',
      services: {
        database: this.db ? 'connected' : 'disconnected',
        ai: 'available',
        storage: 'available'
      }
    });
  }

  /**
   * API documentation endpoint
   */
  apiDocs() {
    return this.success({
      name: 'ChittyTrust API',
      version: '2.0.0',
      description: 'AI-powered trust scoring and evidence processing',
      endpoints: {
        '/api/trust/{personaId}': {
          method: 'GET',
          description: 'Calculate trust score for a persona',
          parameters: {
            personaId: 'string - The persona identifier'
          }
        },
        '/api/trust/{personaId}/timeline': {
          method: 'GET',
          description: 'Get trust score timeline and trends'
        },
        '/api/trust/{personaId}/insights': {
          method: 'GET', 
          description: 'Get AI-powered trust insights'
        },
        '/api/evidence/upload': {
          method: 'POST',
          description: 'Upload evidence for court-admissible storage'
        },
        '/api/evidence/verify': {
          method: 'POST',
          description: 'Verify evidence integrity and authenticity'
        },
        '/api/ai/{model}': {
          method: 'POST',
          description: 'Access Cloudflare Workers AI models'
        }
      },
      authentication: {
        type: 'API Key',
        header: 'X-API-Key'
      },
      rateLimit: {
        requests: 100,
        window: '60 seconds'
      }
    });
  }
}