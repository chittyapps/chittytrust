import os
import logging
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import our trust engine
from src.chitty_trust import calculate_trust
from demo_data import get_persona_data

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chitty-trust-demo-key")

@app.route('/')
def index():
    """Main trust engine dashboard."""
    return render_template('index.html')

@app.route('/api/trust/<persona_id>')
def get_trust_score(persona_id):
    """Calculate trust score for a specific persona."""
    try:
        # Get persona data
        entity, events = get_persona_data(persona_id)
        if not entity:
            return jsonify({'error': 'Persona not found'}), 404
        
        # Calculate trust score using our engine
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        trust_score = loop.run_until_complete(calculate_trust(entity, events))
        loop.close()
        
        # Convert to dict for JSON response
        result = trust_score.to_dict()
        
        # Add persona-specific metadata
        result['persona'] = {
            'id': persona_id,
            'name': entity.name,
            'type': entity.entity_type,
            'chitty_level': get_chitty_level(trust_score.composite_score),
            'verification_status': 'Verified' if entity.identity_verified else 'Unverified'
        }
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error calculating trust for {persona_id}: {str(e)}")
        return jsonify({'error': 'Trust calculation failed'}), 500

@app.route('/api/personas')
def get_personas():
    """Get list of available personas."""
    personas = [
        {
            'id': 'alice',
            'name': 'Alice Community',
            'description': 'High-trust community leader with strong justice focus',
            'type': 'Community Leader',
            'avatar': '👩‍💼'
        },
        {
            'id': 'bob', 
            'name': 'Bob Business',
            'description': 'Mixed business history with dispute resolution experience',
            'type': 'Business Owner',
            'avatar': '👨‍💼'
        },
        {
            'id': 'charlie',
            'name': 'Charlie Changed',
            'description': 'Transformation story - "Shitty to Chitty" journey',
            'type': 'Reformed Individual',
            'avatar': '🔄'
        }
    ]
    return jsonify(personas)

def get_chitty_level(composite_score):
    """Convert composite score to ChittyID level."""
    if composite_score >= 90:
        return {'level': 'L4', 'name': 'Institutional', 'color': '#00ff88'}
    elif composite_score >= 75:
        return {'level': 'L3', 'name': 'Professional', 'color': '#0088ff'}
    elif composite_score >= 50:
        return {'level': 'L2', 'name': 'Enhanced', 'color': '#4444ff'}
    elif composite_score >= 25:
        return {'level': 'L1', 'name': 'Basic', 'color': '#8888ff'}
    else:
        return {'level': 'L0', 'name': 'Anonymous', 'color': '#cccccc'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
