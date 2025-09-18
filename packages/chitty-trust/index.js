/**
 * ChittyTrust - 6D Trust Engine
 * Main entry point for the trust scoring system
 */

export class TrustEngine {
  constructor() {
    this.dimensions = {
      source: { weight: 0.15, name: 'Source Trust' },
      temporal: { weight: 0.10, name: 'Temporal Trust' },
      channel: { weight: 0.15, name: 'Channel Trust' },
      outcome: { weight: 0.20, name: 'Outcome Trust' },
      network: { weight: 0.15, name: 'Network Trust' },
      justice: { weight: 0.25, name: 'Justice Trust' }
    };
  }

  async calculateTrust(entity, events = []) {
    const dimensionScores = this.calculateDimensions(entity, events);
    const outputScores = this.calculateOutputScores(dimensionScores);
    const confidence = this.calculateConfidence(events.length);

    return {
      entity_id: entity.id,
      dimension_scores: dimensionScores,
      output_scores: outputScores,
      composite_score: outputScores.chitty_score,
      confidence,
      chitty_level: this.getChittyLevel(outputScores.chitty_score),
      timestamp: new Date().toISOString()
    };
  }

  calculateDimensions(entity, events) {
    return {
      source: this.calculateSourceTrust(entity),
      temporal: this.calculateTemporalTrust(events),
      channel: this.calculateChannelTrust(entity),
      outcome: this.calculateOutcomeTrust(events),
      network: this.calculateNetworkTrust(entity),
      justice: this.calculateJusticeTrust(entity, events)
    };
  }

  calculateSourceTrust(entity) {
    let score = 50; // Base score
    if (entity.verified_identity) score += 20;
    if (entity.credentials?.length > 0) score += 15;
    if (entity.biometric_verified) score += 15;
    return Math.min(score, 100);
  }

  calculateTemporalTrust(events) {
    if (!events.length) return 50;
    const consistency = this.analyzeConsistency(events);
    const longevity = this.analyzeLongevity(events);
    return (consistency * 0.6 + longevity * 0.4);
  }

  calculateChannelTrust(entity) {
    const channels = entity.communication_channels || [];
    if (!channels.length) return 30;

    const verifiedChannels = channels.filter(c => c.verified).length;
    const ratio = verifiedChannels / channels.length;
    return Math.round(30 + (ratio * 70));
  }

  calculateOutcomeTrust(events) {
    if (!events.length) return 50;

    const positiveOutcomes = events.filter(e => e.outcome === 'positive').length;
    const ratio = positiveOutcomes / events.length;
    return Math.round(ratio * 100);
  }

  calculateNetworkTrust(entity) {
    const connections = entity.network_connections || [];
    if (!connections.length) return 40;

    const trustedConnections = connections.filter(c => c.trust_score > 70).length;
    const ratio = trustedConnections / connections.length;
    return Math.round(40 + (ratio * 60));
  }

  calculateJusticeTrust(entity, events) {
    let score = 50;

    // Justice alignment factors
    if (entity.dispute_resolution_rate > 0.8) score += 20;
    if (entity.transparency_score > 0.7) score += 15;
    if (entity.fairness_rating > 0.75) score += 15;

    return Math.min(score, 100);
  }

  calculateOutputScores(dimensions) {
    return {
      people_score: this.calculatePeopleScore(dimensions),
      legal_score: this.calculateLegalScore(dimensions),
      state_score: this.calculateStateScore(dimensions),
      chitty_score: this.calculateChittyScore(dimensions)
    };
  }

  calculatePeopleScore(dimensions) {
    return Math.round(
      dimensions.network * 0.4 +
      dimensions.outcome * 0.3 +
      dimensions.temporal * 0.3
    );
  }

  calculateLegalScore(dimensions) {
    return Math.round(
      dimensions.justice * 0.5 +
      dimensions.source * 0.3 +
      dimensions.channel * 0.2
    );
  }

  calculateStateScore(dimensions) {
    return Math.round(
      dimensions.source * 0.4 +
      dimensions.justice * 0.4 +
      dimensions.channel * 0.2
    );
  }

  calculateChittyScore(dimensions) {
    let weightedSum = 0;
    for (const [key, value] of Object.entries(dimensions)) {
      weightedSum += value * this.dimensions[key].weight;
    }
    return Math.round(weightedSum);
  }

  calculateConfidence(eventCount) {
    if (eventCount === 0) return 0.3;
    if (eventCount < 5) return 0.5;
    if (eventCount < 20) return 0.7;
    if (eventCount < 50) return 0.85;
    return 0.95;
  }

  getChittyLevel(score) {
    if (score >= 90) return 'L4_INSTITUTIONAL';
    if (score >= 75) return 'L3_PROFESSIONAL';
    if (score >= 50) return 'L2_ENHANCED';
    if (score >= 25) return 'L1_BASIC';
    return 'L0_ANONYMOUS';
  }

  analyzeConsistency(events) {
    if (events.length < 2) return 50;

    let consistencyScore = 0;
    for (let i = 1; i < events.length; i++) {
      const timeDiff = new Date(events[i].timestamp) - new Date(events[i-1].timestamp);
      const expectedInterval = 7 * 24 * 60 * 60 * 1000; // 1 week
      const deviation = Math.abs(timeDiff - expectedInterval) / expectedInterval;
      consistencyScore += Math.max(0, 1 - deviation);
    }

    return Math.round((consistencyScore / (events.length - 1)) * 100);
  }

  analyzeLongevity(events) {
    if (!events.length) return 0;

    const firstEvent = new Date(events[0].timestamp);
    const lastEvent = new Date(events[events.length - 1].timestamp);
    const duration = lastEvent - firstEvent;
    const months = duration / (30 * 24 * 60 * 60 * 1000);

    if (months < 1) return 20;
    if (months < 3) return 40;
    if (months < 6) return 60;
    if (months < 12) return 80;
    return 100;
  }
}

export default TrustEngine;