/**
 * ChittyOS Core Packages Integration
 * Unified entry point for Trust, Verify, and Certify modules
 */

import { TrustEngine } from './chitty-trust/index.js';
import { ChittyVerify } from './chitty-verify/index.js';
import { ChittyCertify } from './chitty-certify/index.js';

// Initialize core services
const trustEngine = new TrustEngine();
const verifyService = new ChittyVerify();
const certifyService = new ChittyCertify();

/**
 * Integrated ChittyOS Core System
 * Combines trust scoring, verification, and certification
 */
export class ChittyCore {
  constructor() {
    this.trust = trustEngine;
    this.verify = verifyService;
    this.certify = certifyService;
  }

  /**
   * Complete user onboarding with verification and trust initialization
   */
  async onboardUser(userId, verificationData) {
    // Step 1: Verify identity
    const verificationResult = await this.verify.verifyUser(
      userId,
      'identity',
      verificationData
    );

    if (!verificationResult.success) {
      return {
        success: false,
        error: 'Identity verification failed',
        details: verificationResult.error
      };
    }

    // Step 2: Initialize trust profile
    const trustEntity = {
      id: userId,
      verified_identity: true,
      credentials: [],
      communication_channels: verificationData.channels || [],
      network_connections: []
    };

    const trustScore = await this.trust.calculateTrust(trustEntity, []);

    // Step 3: Issue onboarding certificate
    const certificate = await this.certify.issueCredential(
      userId,
      'CHITTYOS_IDENTITY',
      {
        claims: {
          verificationId: verificationResult.verificationId,
          trustLevel: trustScore.chitty_level,
          onboardedAt: new Date().toISOString()
        },
        validityDays: 365
      }
    );

    return {
      success: true,
      userId,
      verification: verificationResult,
      trustProfile: trustScore,
      certificate
    };
  }

  /**
   * Verify and certify a document with trust scoring
   */
  async processDocument(userId, document, metadata) {
    // Get user's trust score
    const userEntity = { id: userId, verified_identity: true };
    const trustScore = await this.trust.calculateTrust(userEntity, []);

    // Verify document authenticity
    const verificationResult = await this.verify.verifyDocument({
      documentHash: this.certify.hashDocument(document),
      documentType: metadata.type
    });

    if (!verificationResult.verified) {
      return {
        success: false,
        error: 'Document verification failed'
      };
    }

    // Certify document with trust weighting
    const certificate = await this.certify.certifyDocument(document, {
      ...metadata,
      certifierTrustScore: trustScore.composite_score,
      certifierLevel: trustScore.chitty_level
    });

    return {
      success: true,
      certificate,
      verification: verificationResult,
      trustWeighting: trustScore.composite_score / 100
    };
  }

  /**
   * Create attestation with trust-weighted confidence
   */
  async createTrustedAttestation(attesterId, subject, claims) {
    // Get attester's trust profile
    const attesterEntity = {
      id: attesterId,
      verified_identity: true,
      credentials: []
    };
    const trustScore = await this.trust.calculateTrust(attesterEntity, []);

    // Create attestation with trust weighting
    const attestation = await this.certify.createAttestation(
      subject,
      claims,
      {
        id: attesterId,
        trustScore: trustScore.composite_score,
        verified: true
      }
    );

    return {
      attestation,
      trustWeighting: trustScore.composite_score / 100,
      attesterLevel: trustScore.chitty_level
    };
  }

  /**
   * Comprehensive verification with multi-factor authentication
   */
  async performComprehensiveVerification(userId, verificationData) {
    const results = {
      userId,
      timestamp: new Date().toISOString(),
      verifications: {}
    };

    // Perform all available verifications
    const verificationTypes = ['email', 'phone', 'identity', 'address', 'biometric'];

    for (const type of verificationTypes) {
      if (verificationData[type]) {
        results.verifications[type] = await this.verify.verifyUser(
          userId,
          type,
          verificationData[type]
        );
      }
    }

    // Calculate overall verification score
    const successfulVerifications = Object.values(results.verifications)
      .filter(v => v.success).length;
    const totalVerifications = Object.keys(results.verifications).length;

    results.overallScore = totalVerifications > 0
      ? successfulVerifications / totalVerifications
      : 0;

    // Update trust score based on verifications
    const trustEntity = {
      id: userId,
      verified_identity: results.verifications.identity?.success || false,
      biometric_verified: results.verifications.biometric?.success || false,
      communication_channels: [
        { type: 'email', verified: results.verifications.email?.success || false },
        { type: 'phone', verified: results.verifications.phone?.success || false }
      ]
    };

    results.trustProfile = await this.trust.calculateTrust(trustEntity, []);

    // Issue comprehensive verification certificate if score is high enough
    if (results.overallScore >= 0.6) {
      results.certificate = await this.certify.issueCredential(
        userId,
        'COMPREHENSIVE_VERIFICATION',
        {
          claims: {
            verificationScore: results.overallScore,
            verifiedMethods: Object.keys(results.verifications).filter(
              type => results.verifications[type].success
            ),
            trustLevel: results.trustProfile.chitty_level
          },
          validityDays: 730 // 2 years
        }
      );
    }

    return results;
  }

  /**
   * Get unified trust status for a user
   */
  async getTrustStatus(userId) {
    const entity = { id: userId };
    const trustScore = await this.trust.calculateTrust(entity, []);

    return {
      userId,
      trustScore: trustScore.composite_score,
      trustLevel: trustScore.chitty_level,
      dimensions: trustScore.dimension_scores,
      outputScores: trustScore.output_scores,
      confidence: trustScore.confidence,
      timestamp: trustScore.timestamp
    };
  }
}

// Export individual modules and integrated system
export { TrustEngine, ChittyVerify, ChittyCertify };
export default ChittyCore;