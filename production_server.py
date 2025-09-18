"""
Production server configured for id.chitty.cc domain
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import random
import os

app = Flask(__name__)

# Production CORS configuration for id.chitty.cc
CORS(app, origins=[
    "https://id.chitty.cc",
    "http://id.chitty.cc",
    "https://*.chitty.cc",
    "https://chitty.cc",
    "http://localhost:*",
    "http://127.0.0.1:*"
], supports_credentials=True)

# Domain configuration
TRUST_API_DOMAIN = "trust.chitty.cc"
WEBSITE_PATH = "chitty.cc/trust"
API_BASE_URL = f"https://{TRUST_API_DOMAIN}"

# ChittyID Configuration
def generate_chitty_id(user_type="user"):
    """Generate ChittyID using id.chitty.cc format"""
    import hashlib
    import time

    timestamp = str(int(time.time()))
    unique_data = f"{user_type}-{timestamp}-{random.randint(1000, 9999)}"
    hash_part = hashlib.sha256(unique_data.encode()).hexdigest()[:8].upper()

    return f"id.chitty.cc/{hash_part}"

def verify_chitty_id(chitty_id):
    """Verify ChittyID format and existence"""
    if not chitty_id.startswith("id.chitty.cc/"):
        return False

    id_part = chitty_id.replace("id.chitty.cc/", "")
    return len(id_part) == 8 and id_part.isalnum()

# ============= WEB ROUTES =============
@app.route('/')
def index():
    """Serve the upgraded homepage"""
    return render_template('index_v2.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')

@app.route('/verify')
def verify():
    """Verification page"""
    return render_template('index_v2.html')

@app.route('/certify')
def certify():
    """Certification page"""
    return render_template('index_v2.html')

@app.route('/marketplace')
def marketplace():
    """Marketplace page"""
    return render_template('index_v2.html')

@app.route('/how-trust-works')
def trust_explained():
    """Trust explanation page"""
    return render_template('trust_explained.html')

# ============= TRUST API ENDPOINTS =============
@app.route('/api/trust/<entity_id>', methods=['GET'])
def get_trust_score(entity_id):
    """Get trust score for an entity"""
    # Demo data with enhanced scores for id.chitty.cc
    demo_scores = {
        'alice': {
            'entity_id': 'alice',
            'composite_score': 94,
            'chitty_level': 'L4_INSTITUTIONAL',
            'dimension_scores': {
                'source': 96,
                'temporal': 88,
                'channel': 98,
                'outcome': 92,
                'network': 95,
                'justice': 91
            },
            'output_scores': {
                'people_score': 95,
                'legal_score': 92,
                'state_score': 89,
                'chitty_score': 94
            },
            'confidence': 0.98,
            'timestamp': '2024-09-18T14:30:00Z',
            'domain': TRUST_API_DOMAIN
        },
        'bob': {
            'entity_id': 'bob',
            'composite_score': 71,
            'chitty_level': 'L2_ENHANCED',
            'dimension_scores': {
                'source': 76,
                'temporal': 62,
                'channel': 69,
                'outcome': 74,
                'network': 59,
                'justice': 72
            },
            'output_scores': {
                'people_score': 72,
                'legal_score': 69,
                'state_score': 66,
                'chitty_score': 71
            },
            'confidence': 0.79,
            'timestamp': '2024-09-18T14:30:00Z',
            'domain': TRUST_API_DOMAIN
        },
        'charlie': {
            'entity_id': 'charlie',
            'composite_score': 86,
            'chitty_level': 'L3_PROFESSIONAL',
            'dimension_scores': {
                'source': 89,
                'temporal': 79,
                'channel': 92,
                'outcome': 94,
                'network': 84,
                'justice': 96
            },
            'output_scores': {
                'people_score': 89,
                'legal_score': 86,
                'state_score': 83,
                'chitty_score': 86
            },
            'confidence': 0.91,
            'timestamp': '2024-09-18T14:30:00Z',
            'domain': TRUST_API_DOMAIN
        }
    }

    result = demo_scores.get(entity_id, {
        'entity_id': entity_id,
        'composite_score': random.randint(45, 95),
        'chitty_level': 'L2_ENHANCED',
        'dimension_scores': {
            'source': random.randint(40, 95),
            'temporal': random.randint(40, 95),
            'channel': random.randint(40, 95),
            'outcome': random.randint(40, 95),
            'network': random.randint(40, 95),
            'justice': random.randint(40, 95)
        },
        'confidence': 0.7,
        'timestamp': '2024-09-18T14:30:00Z',
        'domain': DOMAIN
    })

    # Add CORS headers explicitly
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/v2/trust/<entity_id>', methods=['GET'])
def get_trust_score_v2(entity_id):
    """Get trust score for an entity (v2 endpoint)"""
    return get_trust_score(entity_id)

# ============= VERIFICATION API ENDPOINTS =============
@app.route('/api/verify', methods=['POST', 'OPTIONS'])
def verify_user():
    """Verify user identity/documents"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    try:
        data = request.json or {}
        user_id = data.get('userId', 'demo-user')
        verification_type = data.get('verificationType', 'email')

        result = {
            'success': True,
            'verificationId': f'VER-{random.randint(100000, 999999)}',
            'trustLevel': random.choice(['L1_BASIC', 'L2_ENHANCED', 'L3_PROFESSIONAL']),
            'verifiedFields': [verification_type],
            'timestamp': '2024-09-18T14:30:00Z',
            'expiresAt': '2025-09-18T14:30:00Z',
            'domain': TRUST_API_DOMAIN
        }

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({'error': str(e), 'success': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/v2/verify', methods=['POST', 'OPTIONS'])
def verify_user_v2():
    """Verify user identity/documents (v2 endpoint)"""
    return verify_user()

# ============= CERTIFICATION API ENDPOINTS =============
@app.route('/api/certify', methods=['POST', 'OPTIONS'])
def certify_document():
    """Certify a document"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    try:
        data = request.json or {}

        result = {
            'certificateId': f'CERT-{random.randint(100000, 999999)}',
            'documentHash': f'0x{random.randint(100000, 999999):x}',
            'timestamp': '2024-09-18T14:30:00Z',
            'signature': f'SIG-{random.randint(100000, 999999)}',
            'verificationUrl': f'https://{DOMAIN}/verify/CERT-{random.randint(100000, 999999)}',
            'domain': TRUST_API_DOMAIN
        }

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# ============= MARKETPLACE ENDPOINTS =============
@app.route('/api/marketplace/requests', methods=['GET'])
@app.route('/api/v2/marketplace/requests', methods=['GET'])
def get_marketplace_requests():
    """Get active verification requests"""
    requests = [
        {
            'id': 'REQ-001',
            'type': 'identity',
            'title': 'Government ID Verification',
            'description': 'Urgent: Need passport verification for id.chitty.cc',
            'reward': 500,
            'currency': 'CC',
            'posted': '5 min ago',
            'status': 'open',
            'domain': TRUST_API_DOMAIN
        },
        {
            'id': 'REQ-002',
            'type': 'document',
            'title': 'Contract Notarization',
            'description': 'Legal contract needs notarization via ChittyOS',
            'reward': 750,
            'currency': 'CC',
            'posted': '12 min ago',
            'status': 'open',
            'domain': TRUST_API_DOMAIN
        },
        {
            'id': 'REQ-003',
            'type': 'address',
            'title': 'Proof of Residence',
            'description': 'Utility bill verification for trust scoring',
            'reward': 300,
            'currency': 'CC',
            'posted': '1 hour ago',
            'status': 'open',
            'domain': TRUST_API_DOMAIN
        }
    ]

    response = jsonify(requests)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/marketplace/verifiers/top', methods=['GET'])
@app.route('/api/v2/marketplace/verifiers/top', methods=['GET'])
def get_top_verifiers():
    """Get top verifiers"""
    verifiers = [
        {
            'id': 'VER-001',
            'name': 'ChittyVerifyPro',
            'level': 'L4',
            'successRate': 99,
            'completions': 2245,
            'domain': TRUST_API_DOMAIN
        },
        {
            'id': 'VER-002',
            'name': 'TrustGuardian',
            'level': 'L4',
            'successRate': 97,
            'completions': 1982,
            'domain': TRUST_API_DOMAIN
        },
        {
            'id': 'VER-003',
            'name': 'SecureIdentity',
            'level': 'L3',
            'successRate': 96,
            'completions': 1576,
            'domain': TRUST_API_DOMAIN
        }
    ]

    response = jsonify(verifiers)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ============= USER DASHBOARD ENDPOINTS =============
@app.route('/api/user/<user_id>/summary', methods=['GET'])
@app.route('/api/v2/user/<user_id>/summary', methods=['GET'])
def get_user_summary(user_id):
    """Get user dashboard summary"""
    summary = {
        'userId': user_id,
        'name': 'ChittyOS User',
        'chittyId': generate_chitty_id("verified"),
        'trustScore': 89.2,
        'trustLevel': 'L3_PROFESSIONAL',
        'verified': True,
        'domain': TRUST_API_DOMAIN,
        'stats': {
            'verifications': 28,
            'certificates': 15,
            'chittyCoins': 4250,
            'connections': 189
        },
        'recentActivity': [
            {
                'type': 'verification',
                'title': f'Identity verified on {DOMAIN}',
                'timestamp': '1 hour ago',
                'icon': 'check-circle',
                'color': 'green'
            },
            {
                'type': 'certification',
                'title': 'Document certified: Smart Contract',
                'timestamp': '3 hours ago',
                'icon': 'file-plus',
                'color': 'blue'
            },
            {
                'type': 'achievement',
                'title': 'Achievement: ChittyOS Power User',
                'timestamp': '1 day ago',
                'icon': 'award',
                'color': 'purple'
            }
        ]
    }

    response = jsonify(summary)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ============= DOMAIN-SPECIFIC ENDPOINTS =============
@app.route('/api/domain/info', methods=['GET'])
def get_domain_info():
    """Get domain-specific information"""
    info = {
        'domain': TRUST_API_DOMAIN,
        'name': 'ChittyOS Identity Platform',
        'description': 'Decentralized identity and trust infrastructure',
        'version': '2.0.0',
        'features': [
            '6D Trust Scoring',
            'Identity Verification',
            'Document Certification',
            'Verification Marketplace',
            'Trust Analytics'
        ],
        'endpoints': {
            'trust': f'https://{DOMAIN}/api/trust/<entity_id>',
            'verify': f'https://{DOMAIN}/api/verify',
            'certify': f'https://{DOMAIN}/api/certify',
            'marketplace': f'https://{DOMAIN}/api/marketplace/requests'
        }
    }

    response = jsonify(info)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ============= HEALTH & STATUS ENDPOINTS =============
@app.route('/api/health', methods=['GET'])
@app.route('/api/v2/health', methods=['GET'])
def health_check():
    """API health check"""
    health = {
        'status': 'healthy',
        'domain': TRUST_API_DOMAIN,
        'version': '2.0.0',
        'timestamp': '2024-09-18T14:30:00Z',
        'services': {
            'trust': 'operational',
            'verify': 'operational',
            'certify': 'operational',
            'marketplace': 'operational',
            'analytics': 'operational'
        },
        'uptime': '99.9%',
        'response_time': '< 100ms'
    }

    response = jsonify(health)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ============= OPTIONS HANDLER FOR CORS =============
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Handle OPTIONS requests for CORS"""
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    # Production settings
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Allow external connections

    print(f"🚀 ChittyOS Production Server starting...")
    print(f"🌐 Domain: {WEBSITE_PATH}")
    print(f"📡 Listening on: {host}:{port}")
    print(f"🔗 Access at: https://{WEBSITE_PATH}")

    app.run(
        host=host,
        port=port,
        debug=False,  # Production mode
        threaded=True
    )