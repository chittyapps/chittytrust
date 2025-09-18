"""
Trust API Server for trust.chitty.cc
Provides trust scores for ChittyIDs and other entities
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
import hashlib
import time

app = Flask(__name__)

# Configure CORS for chitty.cc ecosystem
CORS(app, origins=[
    "https://chitty.cc",
    "https://*.chitty.cc",
    "https://id.chitty.cc",
    "http://localhost:*",
    "http://127.0.0.1:*"
], supports_credentials=True)

# ============= TRUST ENGINE API =============
@app.route('/api/trust/<entity_id>', methods=['GET'])
def get_trust_score(entity_id):
    """Get trust score for any entity (ChittyID, user, etc.)"""

    # Enhanced demo data for different entity types
    if entity_id.startswith('id.chitty.cc/') or len(entity_id) == 8:
        # ChittyID format
        chitty_id = entity_id.replace('id.chitty.cc/', '') if '/' in entity_id else entity_id

        # Generate consistent scores based on ChittyID
        seed = int(hashlib.sha256(chitty_id.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        base_score = random.randint(60, 95)
        result = {
            'entity_id': f'id.chitty.cc/{chitty_id.upper()}',
            'entity_type': 'chitty_id',
            'composite_score': base_score,
            'chitty_level': get_chitty_level(base_score),
            'dimension_scores': {
                'source': min(95, base_score + random.randint(-10, 15)),
                'temporal': min(95, base_score + random.randint(-15, 10)),
                'channel': min(95, base_score + random.randint(-5, 20)),
                'outcome': min(95, base_score + random.randint(-8, 12)),
                'network': min(95, base_score + random.randint(-12, 18)),
                'justice': min(95, base_score + random.randint(-6, 14))
            },
            'confidence': 0.85 + (base_score - 60) * 0.003,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'api_source': 'trust.chitty.cc'
        }

    elif entity_id in ['alice', 'bob', 'charlie']:
        # Demo personas
        demo_scores = {
            'alice': {
                'entity_id': 'alice',
                'entity_type': 'demo_user',
                'composite_score': 94,
                'chitty_level': 'L4_INSTITUTIONAL',
                'dimension_scores': {
                    'source': 96, 'temporal': 88, 'channel': 98,
                    'outcome': 92, 'network': 95, 'justice': 91
                },
                'confidence': 0.98
            },
            'bob': {
                'entity_id': 'bob',
                'entity_type': 'demo_user',
                'composite_score': 71,
                'chitty_level': 'L2_ENHANCED',
                'dimension_scores': {
                    'source': 76, 'temporal': 62, 'channel': 69,
                    'outcome': 74, 'network': 59, 'justice': 72
                },
                'confidence': 0.79
            },
            'charlie': {
                'entity_id': 'charlie',
                'entity_type': 'demo_user',
                'composite_score': 86,
                'chitty_level': 'L3_PROFESSIONAL',
                'dimension_scores': {
                    'source': 89, 'temporal': 79, 'channel': 92,
                    'outcome': 94, 'network': 84, 'justice': 96
                },
                'confidence': 0.91
            }
        }
        result = demo_scores[entity_id]
        result['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        result['api_source'] = 'trust.chitty.cc'

    else:
        # Generic entity
        hash_seed = int(hashlib.sha256(entity_id.encode()).hexdigest()[:8], 16)
        random.seed(hash_seed)

        score = random.randint(45, 90)
        result = {
            'entity_id': entity_id,
            'entity_type': 'generic',
            'composite_score': score,
            'chitty_level': get_chitty_level(score),
            'dimension_scores': {
                'source': random.randint(40, 95),
                'temporal': random.randint(40, 95),
                'channel': random.randint(40, 95),
                'outcome': random.randint(40, 95),
                'network': random.randint(40, 95),
                'justice': random.randint(40, 95)
            },
            'confidence': 0.7,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'api_source': 'trust.chitty.cc'
        }

    # Calculate output scores
    dims = result['dimension_scores']
    result['output_scores'] = {
        'people_score': round((dims['network'] * 0.4 + dims['outcome'] * 0.3 + dims['temporal'] * 0.3)),
        'legal_score': round((dims['justice'] * 0.5 + dims['source'] * 0.3 + dims['channel'] * 0.2)),
        'state_score': round((dims['source'] * 0.4 + dims['justice'] * 0.4 + dims['channel'] * 0.2)),
        'chitty_score': result['composite_score']
    }

    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

def get_chitty_level(score):
    """Convert numeric score to ChittyID trust level"""
    if score >= 90: return 'L4_INSTITUTIONAL'
    if score >= 75: return 'L3_PROFESSIONAL'
    if score >= 50: return 'L2_ENHANCED'
    if score >= 25: return 'L1_BASIC'
    return 'L0_ANONYMOUS'

@app.route('/api/trust/batch', methods=['POST'])
def get_batch_trust_scores():
    """Get trust scores for multiple entities"""
    data = request.json or {}
    entity_ids = data.get('entities', [])

    results = []
    for entity_id in entity_ids[:50]:  # Limit to 50 entities
        try:
            # Reuse the single entity logic
            response = get_trust_score(entity_id)
            results.append(response.get_json())
        except:
            results.append({
                'entity_id': entity_id,
                'error': 'Unable to calculate trust score'
            })

    response = jsonify({
        'count': len(results),
        'results': results,
        'api_source': 'trust.chitty.cc'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/trust/search', methods=['GET'])
def search_trusted_entities():
    """Search for entities by trust criteria"""
    min_score = int(request.args.get('min_score', 70))
    max_score = int(request.args.get('max_score', 100))
    entity_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 10))

    # Generate mock search results
    results = []
    for i in range(limit):
        score = random.randint(min_score, max_score)
        entity_id = f"id.chitty.cc/{hashlib.sha256(str(i).encode()).hexdigest()[:8].upper()}"

        results.append({
            'entity_id': entity_id,
            'composite_score': score,
            'chitty_level': get_chitty_level(score),
            'entity_type': 'chitty_id'
        })

    response = jsonify({
        'query': {
            'min_score': min_score,
            'max_score': max_score,
            'type': entity_type
        },
        'count': len(results),
        'results': results
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/trust/analytics/<entity_id>', methods=['GET'])
def get_trust_analytics(entity_id):
    """Get detailed trust analytics for an entity"""
    # Get base trust data
    trust_data = get_trust_score(entity_id).get_json()

    # Add analytics
    analytics = {
        'trends': {
            'last_30_days': [random.randint(trust_data['composite_score']-10, trust_data['composite_score']+5) for _ in range(30)],
            'direction': random.choice(['increasing', 'stable', 'decreasing']),
            'volatility': random.choice(['low', 'medium', 'high'])
        },
        'comparisons': {
            'peer_average': random.randint(60, 85),
            'network_rank': random.randint(1, 100),
            'percentile': random.randint(70, 95)
        },
        'recommendations': [
            'Increase network connections',
            'Complete additional verifications',
            'Improve response consistency'
        ]
    }

    result = {
        **trust_data,
        'analytics': analytics
    }

    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'trust-engine',
        'domain': 'trust.chitty.cc',
        'version': '1.0.0',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'endpoints': {
            'trust_score': '/api/trust/<entity_id>',
            'batch_scores': '/api/trust/batch',
            'search': '/api/trust/search',
            'analytics': '/api/trust/analytics/<entity_id>'
        }
    })

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        'title': 'ChittyOS Trust Engine API',
        'description': 'Trust scoring service for the ChittyOS ecosystem',
        'base_url': 'https://trust.chitty.cc',
        'endpoints': {
            'GET /api/trust/<entity_id>': 'Get trust score for an entity',
            'POST /api/trust/batch': 'Get trust scores for multiple entities',
            'GET /api/trust/search': 'Search entities by trust criteria',
            'GET /api/trust/analytics/<entity_id>': 'Get detailed trust analytics',
            'GET /api/health': 'Service health check'
        },
        'usage_examples': {
            'chitty_id': 'https://trust.chitty.cc/api/trust/id.chitty.cc/ABC12345',
            'user': 'https://trust.chitty.cc/api/trust/alice',
            'batch': 'POST https://trust.chitty.cc/api/trust/batch {"entities": ["alice", "bob"]}'
        }
    })

# Handle OPTIONS for CORS
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == '__main__':
    print("🚀 ChittyOS Trust Engine API starting...")
    print("🌐 Service: trust.chitty.cc")
    print("📊 Providing trust scores for ChittyIDs and entities")

    app.run(
        host='0.0.0.0',
        port=5003,
        debug=False,
        threaded=True
    )