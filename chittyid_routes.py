"""
ChittyID specific routes and functionality for id.chitty.cc
"""

from flask import Flask, jsonify, request, render_template, redirect, url_for
import hashlib
import time
import random
import json

def add_chittyid_routes(app):
    """Add ChittyID specific routes to the Flask app"""

    @app.route('/id/<chitty_id>')
    def view_chitty_id(chitty_id):
        """View a specific ChittyID profile"""
        # Verify the ChittyID format
        if not chitty_id.isalnum() or len(chitty_id) != 8:
            return render_template('error.html', error="Invalid ChittyID format"), 404

        full_chitty_id = f"id.chitty.cc/{chitty_id.upper()}"

        # Generate mock profile data
        profile = {
            'chittyId': full_chitty_id,
            'shortId': chitty_id.upper(),
            'name': f'ChittyOS User {chitty_id[:4].upper()}',
            'trustScore': random.randint(65, 95),
            'trustLevel': random.choice(['L2_ENHANCED', 'L3_PROFESSIONAL', 'L4_INSTITUTIONAL']),
            'verified': True,
            'joinDate': '2024-09-18',
            'verifications': {
                'email': True,
                'phone': True,
                'identity': random.choice([True, False]),
                'biometric': random.choice([True, False])
            },
            'stats': {
                'certificates': random.randint(5, 25),
                'verifications': random.randint(10, 50),
                'connections': random.randint(20, 200),
                'chittyCoins': random.randint(1000, 10000)
            },
            'achievements': [
                'Trust Builder',
                'Verified Identity',
                'Community Member'
            ],
            'publicKey': f'0x{chitty_id.lower()}...{random.randint(1000, 9999)}'
        }

        return render_template('chittyid_profile.html', profile=profile)

    @app.route('/create-id')
    def create_chitty_id():
        """Create a new ChittyID"""
        return render_template('create_chittyid.html')

    @app.route('/api/chittyid/create', methods=['POST'])
    def api_create_chitty_id():
        """API endpoint to create a new ChittyID"""
        data = request.json or {}
        user_type = data.get('type', 'user')
        name = data.get('name', 'Anonymous User')

        # Generate new ChittyID
        timestamp = str(int(time.time()))
        unique_data = f"{user_type}-{name}-{timestamp}-{random.randint(1000, 9999)}"
        hash_part = hashlib.sha256(unique_data.encode()).hexdigest()[:8].upper()

        chitty_id = f"id.chitty.cc/{hash_part}"
        short_id = hash_part

        result = {
            'success': True,
            'chittyId': chitty_id,
            'shortId': short_id,
            'profileUrl': f"https://id.chitty.cc/id/{short_id}",
            'qrCode': f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={chitty_id}",
            'created': timestamp,
            'type': user_type
        }

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    @app.route('/api/chittyid/<chitty_id>/verify', methods=['POST'])
    def api_verify_chitty_id(chitty_id):
        """Verify a ChittyID"""
        data = request.json or {}
        verification_type = data.get('type', 'existence')

        if not chitty_id.isalnum() or len(chitty_id) != 8:
            return jsonify({'valid': False, 'error': 'Invalid ChittyID format'}), 400

        result = {
            'valid': True,
            'chittyId': f"id.chitty.cc/{chitty_id.upper()}",
            'exists': True,
            'trustScore': random.randint(65, 95),
            'verified': True,
            'lastActivity': '2024-09-18T14:30:00Z'
        }

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    @app.route('/api/chittyid/resolve/<path:identifier>')
    def api_resolve_chitty_id(identifier):
        """Resolve various ChittyID formats"""
        # Handle different formats:
        # - id.chitty.cc/ABC12345
        # - ABC12345
        # - @username

        if identifier.startswith('id.chitty.cc/'):
            short_id = identifier.replace('id.chitty.cc/', '')
        elif identifier.startswith('@'):
            # Handle username lookup (mock)
            username = identifier[1:]
            short_id = hashlib.sha256(username.encode()).hexdigest()[:8].upper()
        else:
            short_id = identifier.upper()

        if not short_id.isalnum() or len(short_id) != 8:
            return jsonify({'error': 'Invalid identifier format'}), 400

        result = {
            'resolved': True,
            'chittyId': f"id.chitty.cc/{short_id}",
            'shortId': short_id,
            'profileUrl': f"https://id.chitty.cc/id/{short_id}",
            'trustScore': random.randint(65, 95),
            'verified': True
        }

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    @app.route('/api/chittyid/search')
    def api_search_chitty_ids():
        """Search for ChittyIDs"""
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))

        # Mock search results
        results = []
        for i in range(min(limit, 5)):
            random_id = hashlib.sha256(f"{query}-{i}".encode()).hexdigest()[:8].upper()
            results.append({
                'chittyId': f"id.chitty.cc/{random_id}",
                'shortId': random_id,
                'name': f"User {random_id[:4]}",
                'trustScore': random.randint(65, 95),
                'verified': random.choice([True, False]),
                'profileUrl': f"https://id.chitty.cc/id/{random_id}"
            })

        response = jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    @app.route('/qr/<chitty_id>')
    def generate_qr_code(chitty_id):
        """Generate QR code for ChittyID"""
        if not chitty_id.isalnum() or len(chitty_id) != 8:
            return "Invalid ChittyID", 400

        full_id = f"id.chitty.cc/{chitty_id.upper()}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={full_id}"

        return redirect(qr_url)

    return app