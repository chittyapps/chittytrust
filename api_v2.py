"""
ChittyOS API v2 - Enhanced endpoints for new package functionality
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import asyncio
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import packages directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages'))
import packages.index as packages
ChittyCore = packages.ChittyCore

app = Flask(__name__)
CORS(app)

# Initialize ChittyCore
chitty_core = ChittyCore()

# ============= WEB ROUTES =============
@app.route('/')
def index():
    """Serve the upgraded homepage"""
    return render_template('index_v2.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')

# ============= TRUST API ENDPOINTS =============
@app.route('/api/v2/trust/<entity_id>', methods=['GET'])
def get_trust_score(entity_id):
    """Get trust score for an entity"""
    try:
        # Run async trust calculation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Demo entities for testing
        demo_entities = {
            'alice': {
                'id': 'alice',
                'verified_identity': True,
                'credentials': ['professional', 'verified_email'],
                'biometric_verified': True,
                'communication_channels': [
                    {'type': 'email', 'verified': True},
                    {'type': 'phone', 'verified': True}
                ],
                'network_connections': [
                    {'id': 'conn1', 'trust_score': 95},
                    {'id': 'conn2', 'trust_score': 88}
                ],
                'dispute_resolution_rate': 0.95,
                'transparency_score': 0.9,
                'fairness_rating': 0.92
            },
            'bob': {
                'id': 'bob',
                'verified_identity': True,
                'credentials': ['basic'],
                'biometric_verified': False,
                'communication_channels': [
                    {'type': 'email', 'verified': True}
                ],
                'network_connections': [
                    {'id': 'conn1', 'trust_score': 70}
                ],
                'dispute_resolution_rate': 0.7,
                'transparency_score': 0.6,
                'fairness_rating': 0.65
            },
            'charlie': {
                'id': 'charlie',
                'verified_identity': True,
                'credentials': ['professional', 'mentor'],
                'biometric_verified': True,
                'communication_channels': [
                    {'type': 'email', 'verified': True},
                    {'type': 'phone', 'verified': True},
                    {'type': 'linkedin', 'verified': True}
                ],
                'network_connections': [
                    {'id': 'conn1', 'trust_score': 90},
                    {'id': 'conn2', 'trust_score': 92},
                    {'id': 'conn3', 'trust_score': 88}
                ],
                'dispute_resolution_rate': 0.85,
                'transparency_score': 0.8,
                'fairness_rating': 0.83
            }
        }

        entity = demo_entities.get(entity_id, {'id': entity_id})

        # Demo events for testing
        events = []
        if entity_id == 'alice':
            events = [
                {'timestamp': '2024-01-01T00:00:00Z', 'outcome': 'positive'},
                {'timestamp': '2024-02-01T00:00:00Z', 'outcome': 'positive'},
                {'timestamp': '2024-03-01T00:00:00Z', 'outcome': 'positive'}
            ]

        result = loop.run_until_complete(chitty_core.trust.calculateTrust(entity, events))
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/trust/status/<user_id>', methods=['GET'])
def get_trust_status(user_id):
    """Get comprehensive trust status for a user"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(chitty_core.getTrustStatus(user_id))
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= VERIFICATION API ENDPOINTS =============
@app.route('/api/v2/verify', methods=['POST'])
def verify_user():
    """Verify user identity/documents"""
    try:
        data = request.json
        user_id = data.get('userId')
        verification_type = data.get('verificationType')
        verification_data = data.get('data')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.verify.verifyUser(user_id, verification_type, verification_data)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/verify/comprehensive', methods=['POST'])
def comprehensive_verification():
    """Perform comprehensive multi-factor verification"""
    try:
        data = request.json
        user_id = data.get('userId')
        verification_data = data.get('verificationData')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.performComprehensiveVerification(user_id, verification_data)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/verify/status/<verification_id>', methods=['GET'])
def check_verification(verification_id):
    """Check verification status"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.verify.checkVerificationStatus(verification_id)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CERTIFICATION API ENDPOINTS =============
@app.route('/api/v2/certify/document', methods=['POST'])
def certify_document():
    """Certify a document"""
    try:
        data = request.json
        document = data.get('document')
        metadata = data.get('metadata', {})

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.certify.certifyDocument(document, metadata)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/certify/credential', methods=['POST'])
def issue_credential():
    """Issue a credential"""
    try:
        data = request.json
        recipient_id = data.get('recipientId')
        credential_type = data.get('credentialType')
        credential_data = data.get('data')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.certify.issueCredential(recipient_id, credential_type, credential_data)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/certify/attestation', methods=['POST'])
def create_attestation():
    """Create an attestation"""
    try:
        data = request.json
        attester_id = data.get('attesterId')
        subject = data.get('subject')
        claims = data.get('claims')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.createTrustedAttestation(attester_id, subject, claims)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/certify/achievement', methods=['POST'])
def certify_achievement():
    """Certify an achievement"""
    try:
        data = request.json
        user_id = data.get('userId')
        achievement = data.get('achievement')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.certify.certifyAchievement(user_id, achievement)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/certify/verify/<certificate_id>', methods=['POST'])
def verify_certificate(certificate_id):
    """Verify a certificate"""
    try:
        data = request.json
        signature = data.get('signature')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.certify.verifyCertificate(certificate_id, signature)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= INTEGRATED ENDPOINTS =============
@app.route('/api/v2/onboard', methods=['POST'])
def onboard_user():
    """Complete user onboarding with verification and trust initialization"""
    try:
        data = request.json
        user_id = data.get('userId')
        verification_data = data.get('verificationData')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.onboardUser(user_id, verification_data)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/process-document', methods=['POST'])
def process_document():
    """Process and certify a document with trust scoring"""
    try:
        data = request.json
        user_id = data.get('userId')
        document = data.get('document')
        metadata = data.get('metadata')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            chitty_core.processDocument(user_id, document, metadata)
        )
        loop.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= MARKETPLACE ENDPOINTS =============
@app.route('/api/v2/marketplace/requests', methods=['GET'])
def get_marketplace_requests():
    """Get active verification requests"""
    # Mock data for demonstration
    requests = [
        {
            'id': 'REQ-001',
            'type': 'identity',
            'title': 'Government ID Verification',
            'description': 'Urgent: Need passport verification',
            'reward': 500,
            'currency': 'CC',
            'posted': '5 min ago',
            'status': 'open'
        },
        {
            'id': 'REQ-002',
            'type': 'document',
            'title': 'Contract Notarization',
            'description': 'Legal contract needs notarization',
            'reward': 750,
            'currency': 'CC',
            'posted': '12 min ago',
            'status': 'open'
        },
        {
            'id': 'REQ-003',
            'type': 'address',
            'title': 'Proof of Residence',
            'description': 'Utility bill verification needed',
            'reward': 300,
            'currency': 'CC',
            'posted': '1 hour ago',
            'status': 'open'
        }
    ]

    return jsonify(requests)

@app.route('/api/v2/marketplace/verifiers/top', methods=['GET'])
def get_top_verifiers():
    """Get top verifiers"""
    verifiers = [
        {
            'id': 'VER-001',
            'name': 'VerifyPro',
            'level': 'L4',
            'successRate': 98,
            'completions': 1245,
            'avatar': None
        },
        {
            'id': 'VER-002',
            'name': 'TrustGuard',
            'level': 'L3',
            'successRate': 95,
            'completions': 982,
            'avatar': None
        },
        {
            'id': 'VER-003',
            'name': 'SecureID',
            'level': 'L3',
            'successRate': 94,
            'completions': 876,
            'avatar': None
        }
    ]

    return jsonify(verifiers)

# ============= USER DASHBOARD ENDPOINTS =============
@app.route('/api/v2/user/<user_id>/summary', methods=['GET'])
def get_user_summary(user_id):
    """Get user dashboard summary"""
    # Mock data for demonstration
    summary = {
        'userId': user_id,
        'name': 'John Doe',
        'chittyId': 'CHT-2024-A1B2C3',
        'trustScore': 87.5,
        'trustLevel': 'L3_PROFESSIONAL',
        'verified': True,
        'stats': {
            'verifications': 24,
            'certificates': 12,
            'chittyCoins': 3450,
            'connections': 156
        },
        'recentActivity': [
            {
                'type': 'verification',
                'title': 'Identity verification completed',
                'timestamp': '2 hours ago',
                'icon': 'check-circle',
                'color': 'green'
            },
            {
                'type': 'certification',
                'title': 'Document certified: Employment Contract',
                'timestamp': '1 day ago',
                'icon': 'file-plus',
                'color': 'blue'
            },
            {
                'type': 'achievement',
                'title': 'Achievement unlocked: Trust Builder',
                'timestamp': '3 days ago',
                'icon': 'award',
                'color': 'purple'
            }
        ]
    }

    return jsonify(summary)

# ============= HEALTH & STATUS ENDPOINTS =============
@app.route('/api/v2/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'services': {
            'trust': 'operational',
            'verify': 'operational',
            'certify': 'operational',
            'marketplace': 'operational'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)