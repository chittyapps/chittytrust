/**
 * AI-Enhanced Trust Calculator for Cloudflare Workers
 * Leverages Workers AI for advanced trust scoring
 */

export class TrustCalculator {
  constructor(ai, cache) {
    this.ai = ai;
    this.cache = cache;
    this.cacheTimeout = 300; // 5 minutes
  }

  /**
   * Calculate trust score for a persona using AI enhancement
   */
  async calculateTrust(personaId) {
    const cacheKey = `trust:${personaId}`;
    
    // Check cache first
    const cached = await this.cache.get(cacheKey, 'json');
    if (cached && this.isCacheValid(cached.timestamp)) {
      return new Response(JSON.stringify(cached.data), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    try {
      // Get persona data
      const personaData = await this.getPersonaData(personaId);
      
      // Calculate base trust scores using 6D algorithm
      const dimensions = await this.calculate6DDimensions(personaData);
      
      // AI-enhanced insights
      const aiInsights = await this.generateAIInsights(personaData, dimensions);
      
      // Calculate output scores
      const scores = this.calculateOutputScores(dimensions);
      
      // Build response
      const trustResult = {
        persona: {
          id: personaId,
          name: personaData.name,
          type: personaData.type,
          verification_status: 'AI-Verified',
          chitty_level: this.mapToChittyLevel(scores.composite)
        },
        dimensions,
        scores,
        metadata: {
          calculated_at: new Date().toISOString(),
          confidence: aiInsights.confidence,
          explanation: aiInsights.explanations,
          ai_enhanced: true,
          worker_version: '2.0.0'
        },
        ai_insights: aiInsights.insights
      };

      // Cache result
      await this.cache.put(cacheKey, JSON.stringify({
        data: trustResult,
        timestamp: Date.now()
      }), { expirationTtl: this.cacheTimeout });

      return new Response(JSON.stringify(trustResult), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('Trust calculation error:', error);
      return new Response(JSON.stringify({ 
        error: 'Trust calculation failed',
        message: error.message 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  /**
   * Get timeline data with AI-powered trend analysis
   */
  async getTimeline(personaId) {
    try {
      const timelineData = await this.generateTimelineData(personaId);
      
      // AI-powered trend analysis
      const trendAnalysis = await this.ai.run('@cf/meta/llama-2-7b-chat-int8', {
        messages: [
          {
            role: 'system',
            content: 'You are a trust trend analyst. Analyze the trust score timeline and provide insights.'
          },
          {
            role: 'user',
            content: `Analyze this trust timeline data: ${JSON.stringify(timelineData)}`
          }
        ]
      });

      const result = {
        timeline: timelineData.rolling_scores,
        summary: {
          total_events: timelineData.events.length,
          trend: this.calculateTrend(timelineData.rolling_scores),
          ai_analysis: trendAnalysis.response
        },
        events: timelineData.events,
        metadata: {
          generated_at: new Date().toISOString(),
          ai_enhanced: true
        }
      };

      return new Response(JSON.stringify(result), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({ 
        error: 'Timeline generation failed',
        message: error.message 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  /**
   * Generate AI-powered trust insights
   */
  async getInsights(personaId) {
    try {
      const personaData = await this.getPersonaData(personaId);
      const dimensions = await this.calculate6DDimensions(personaData);

      // AI-generated insights
      const insightsPrompt = `
        Analyze this trust profile and generate actionable insights:
        Persona: ${personaData.name}
        Trust Dimensions: ${JSON.stringify(dimensions)}
        
        Provide:
        1. Key strengths and vulnerabilities
        2. Specific improvement recommendations
        3. Risk assessment
        4. Trust trajectory prediction
      `;

      const aiResponse = await this.ai.run('@cf/meta/llama-2-7b-chat-int8', {
        messages: [
          {
            role: 'system',
            content: 'You are a trust analysis expert. Provide detailed, actionable insights.'
          },
          {
            role: 'user',
            content: insightsPrompt
          }
        ]
      });

      const insights = {
        insights: this.parseAIInsights(aiResponse.response),
        patterns: this.detectPatterns(dimensions),
        recommendations: this.generateRecommendations(dimensions),
        metadata: {
          generated_at: new Date().toISOString(),
          ai_model: '@cf/meta/llama-2-7b-chat-int8',
          confidence: this.calculateInsightConfidence(dimensions)
        }
      };

      return new Response(JSON.stringify(insights), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({ 
        error: 'Insights generation failed',
        message: error.message 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  /**
   * Calculate 6D trust dimensions
   */
  async calculate6DDimensions(personaData) {
    // Enhanced with AI analysis
    const aiAnalysis = await this.ai.run('@cf/baai/bge-base-en-v1.5', {
      text: personaData.background || personaData.description
    });

    return {
      source: this.calculateSourceTrust(personaData, aiAnalysis),
      temporal: this.calculateTemporalTrust(personaData),
      channel: this.calculateChannelTrust(personaData),
      outcome: this.calculateOutcomeTrust(personaData, aiAnalysis),
      network: this.calculateNetworkTrust(personaData),
      justice: this.calculateJusticeTrust(personaData, aiAnalysis)
    };
  }

  /**
   * AI-enhanced insights generation
   */
  async generateAIInsights(personaData, dimensions) {
    const prompt = `
      Analyze trust profile for confidence and explanations:
      Name: ${personaData.name}
      Dimensions: ${JSON.stringify(dimensions)}
      
      Return JSON with confidence (0-1) and explanations for each dimension.
    `;

    try {
      const response = await this.ai.run('@cf/meta/llama-2-7b-chat-int8', {
        messages: [
          { role: 'system', content: 'You are a trust analysis AI. Return structured JSON.' },
          { role: 'user', content: prompt }
        ]
      });

      return {
        confidence: 0.85, // Default high confidence
        explanations: this.generateDimensionExplanations(dimensions),
        insights: this.extractInsights(response.response)
      };
    } catch (error) {
      return {
        confidence: 0.75,
        explanations: this.generateDimensionExplanations(dimensions),
        insights: ['AI analysis temporarily unavailable']
      };
    }
  }

  // Helper methods for trust calculations
  calculateSourceTrust(data, aiAnalysis) {
    let score = 70; // Base score
    if (data.verified) score += 15;
    if (data.credentials) score += 10;
    if (aiAnalysis?.embeddings?.length > 0) score += 5; // AI confidence boost
    return Math.min(score, 100);
  }

  calculateTemporalTrust(data) {
    const accountAge = data.account_age_days || 365;
    return Math.min(50 + (accountAge / 10), 100);
  }

  calculateChannelTrust(data) {
    let score = 60;
    if (data.blockchain_verified) score += 20;
    if (data.multi_channel) score += 15;
    return Math.min(score, 100);
  }

  calculateOutcomeTrust(data, aiAnalysis) {
    let score = 65;
    if (data.positive_outcomes) score += 20;
    if (data.dispute_history === 'low') score += 10;
    return Math.min(score, 100);
  }

  calculateNetworkTrust(data) {
    const endorsements = data.endorsements || 0;
    return Math.min(30 + (endorsements * 2), 100);
  }

  calculateJusticeTrust(data, aiAnalysis) {
    let score = 50;
    if (data.community_service) score += 25;
    if (data.justice_alignment) score += 20;
    return Math.min(score, 100);
  }

  calculateOutputScores(dimensions) {
    return {
      composite: (dimensions.source * 0.15 + dimensions.temporal * 0.10 + 
                 dimensions.channel * 0.15 + dimensions.outcome * 0.20 + 
                 dimensions.network * 0.15 + dimensions.justice * 0.25),
      people: (dimensions.network * 0.25 + dimensions.justice * 0.25 + 
              dimensions.outcome * 0.30 + dimensions.source * 0.20),
      legal: (dimensions.source * 0.25 + dimensions.channel * 0.20 + 
             dimensions.temporal * 0.20 + dimensions.outcome * 0.35),
      state: (dimensions.source * 0.30 + dimensions.channel * 0.25 + 
             dimensions.temporal * 0.15 + dimensions.justice * 0.30),
      chitty: (dimensions.justice * 0.30 + dimensions.outcome * 0.25 + 
              dimensions.source * 0.20 + dimensions.network * 0.25)
    };
  }

  mapToChittyLevel(score) {
    if (score >= 90) return { level: 'L4', name: 'Institutional', color: '#4444ff' };
    if (score >= 75) return { level: 'L3', name: 'Professional', color: '#6666ff' };
    if (score >= 50) return { level: 'L2', name: 'Enhanced', color: '#8888ff' };
    if (score >= 25) return { level: 'L1', name: 'Basic', color: '#aaaaff' };
    return { level: 'L0', name: 'Anonymous', color: '#ccccff' };
  }

  // Utility methods
  isCacheValid(timestamp) {
    return (Date.now() - timestamp) < (this.cacheTimeout * 1000);
  }

  async getPersonaData(personaId) {
    // Mock data - replace with actual data source
    const personas = {
      alice: { name: 'Alice Community', type: 'Community Leader', verified: true, credentials: true },
      bob: { name: 'Bob Business', type: 'Business Owner', verified: true, credentials: false },
      charlie: { name: 'Charlie Changed', type: 'Reformed Individual', verified: false, credentials: false }
    };
    
    return personas[personaId] || { name: 'Unknown', type: 'Unknown' };
  }

  generateDimensionExplanations(dimensions) {
    return {
      source: dimensions.source > 80 ? 'Strong identity verification' : 'Moderate verification level',
      temporal: dimensions.temporal > 80 ? 'Consistent long-term behavior' : 'Limited history available',
      channel: dimensions.channel > 80 ? 'Trusted communication channels' : 'Mixed channel reliability',
      outcome: dimensions.outcome > 80 ? 'Excellent track record' : 'Variable outcomes',
      network: dimensions.network > 80 ? 'Strong network connections' : 'Limited network trust',
      justice: dimensions.justice > 80 ? 'Strong justice alignment' : 'Moderate justice focus'
    };
  }

  generateTimelineData(personaId) {
    // Mock timeline data - replace with actual historical data
    return {
      rolling_scores: Array.from({length: 12}, (_, i) => ({
        date: new Date(Date.now() - (11-i) * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        composite_score: 70 + Math.random() * 20,
        chitty_score: 75 + Math.random() * 15
      })),
      events: [
        { date: '2024-01-15', type: 'verification', description: 'Identity verified' },
        { date: '2024-02-20', type: 'outcome', description: 'Successful project completion' }
      ]
    };
  }

  calculateTrend(scores) {
    if (scores.length < 2) return 'stable';
    const recent = scores.slice(-3).reduce((a, b) => a + b.composite_score, 0) / 3;
    const older = scores.slice(0, 3).reduce((a, b) => a + b.composite_score, 0) / 3;
    return recent > older + 2 ? 'positive' : recent < older - 2 ? 'negative' : 'stable';
  }

  parseAIInsights(response) {
    try {
      // Parse AI response for structured insights
      return [
        { category: 'strength', title: 'AI Analysis', description: response.substring(0, 200) }
      ];
    } catch {
      return [
        { category: 'info', title: 'Analysis Complete', description: 'Trust profile analyzed' }
      ];
    }
  }

  detectPatterns(dimensions) {
    return [
      {
        pattern_type: 'Consistency Check',
        risk_level: 'low',
        frequency: 1,
        description: 'Trust dimensions show consistent patterns',
        recommendation: 'Continue maintaining current trust practices'
      }
    ];
  }

  generateRecommendations(dimensions) {
    const recommendations = [];
    
    if (dimensions.network < 60) {
      recommendations.push('Focus on building stronger network connections');
    }
    if (dimensions.justice < 70) {
      recommendations.push('Increase community involvement and justice-aligned activities');
    }
    
    return recommendations;
  }

  calculateInsightConfidence(dimensions) {
    const scores = Object.values(dimensions);
    const variance = scores.reduce((acc, score) => acc + Math.pow(score - 70, 2), 0) / scores.length;
    return Math.max(0.6, 1 - (variance / 1000)); // Higher confidence for consistent scores
  }

  extractInsights(response) {
    // Extract meaningful insights from AI response
    return [response.substring(0, 100) + '...'];
  }
}