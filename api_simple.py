"""
Simple API server to test upgraded website
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import random

app = Flask(__name__)

# Configure CORS for id.chitty.cc domain
CORS(app, origins=[
    "https://id.chitty.cc",
    "http://id.chitty.cc",
    "https://*.chitty.cc",
    "http://localhost:*",
    "http://127.0.0.1:*"
])

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
@app.route('/api/trust/<entity_id>', methods=['GET'])
def get_trust_score(entity_id):
    """Get trust score for an entity"""
    # Demo data
    demo_scores = {
        'alice': {
            'entity_id': 'alice',
            'composite_score': 89,
            'chitty_level': 'L4_INSTITUTIONAL',
            'dimension_scores': {
                'source': 92,
                'temporal': 78,
                'channel': 95,
                'outcome': 88,
                'network': 91,
                'justice': 86
            },
            'output_scores': {
                'people_score': 92,
                'legal_score': 88,
                'state_score': 85,
                'chitty_score': 89
            },
            'confidence': 0.95,
            'timestamp': '2024-09-18T14:30:00Z'
        },
        'bob': {
            'entity_id': 'bob',
            'composite_score': 67,
            'chitty_level': 'L2_ENHANCED',
            'dimension_scores': {
                'source': 72,
                'temporal': 58,
                'channel': 65,
                'outcome': 70,
                'network': 55,
                'justice': 68
            },
            'output_scores': {
                'people_score': 68,
                'legal_score': 65,
                'state_score': 62,
                'chitty_score': 67
            },
            'confidence': 0.75,
            'timestamp': '2024-09-18T14:30:00Z'
        },
        'charlie': {
            'entity_id': 'charlie',
            'composite_score': 82,
            'chitty_level': 'L3_PROFESSIONAL',
            'dimension_scores': {
                'source': 85,
                'temporal': 75,
                'channel': 88,
                'outcome': 90,
                'network': 80,
                'justice': 92
            },
            'output_scores': {
                'people_score': 85,
                'legal_score': 82,
                'state_score': 79,
                'chitty_score': 82
            },
            'confidence': 0.88,
            'timestamp': '2024-09-18T14:30:00Z'
        }
    }

    return jsonify(demo_scores.get(entity_id, {
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
        'timestamp': '2024-09-18T14:30:00Z'
    }))

# ============= MARKETPLACE ENDPOINTS =============
@app.route('/api/v2/marketplace/requests', methods=['GET'])
def get_marketplace_requests():
    """Get active verification requests"""
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