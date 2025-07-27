import os
import logging
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import our trust engine
from src.chitty_trust import calculate_trust
from src.chitty_trust.analytics import TrustAnalytics
from src.chitty_trust.visualization import TrustVisualizationEngine
from demo_data import get_persona_data

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chitty-trust-demo-key")

# Initialize analytics engines
analytics_engine = TrustAnalytics()
viz_engine = TrustVisualizationEngine()

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

@app.route('/api/trust/<persona_id>/insights')
def get_trust_insights(persona_id):
    """Get detailed trust insights and analytics for a persona."""
    try:
        # Get persona data
        entity, events = get_persona_data(persona_id)
        if not entity:
            return jsonify({'error': 'Persona not found'}), 404
        
        # Calculate trust score first
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        trust_score = loop.run_until_complete(calculate_trust(entity, events))
        
        # Generate insights
        dimension_scores = {
            "source": trust_score.source_score,
            "temporal": trust_score.temporal_score,  
            "channel": trust_score.channel_score,
            "outcome": trust_score.outcome_score,
            "network": trust_score.network_score,
            "justice": trust_score.justice_score,
        }
        
        insights = loop.run_until_complete(
            analytics_engine.generate_insights(entity, events, dimension_scores)
        )
        
        patterns = loop.run_until_complete(
            analytics_engine.detect_patterns(entity, events)
        )
        
        confidence_intervals = analytics_engine.calculate_confidence_intervals(
            dimension_scores, events
        )
        
        loop.close()
        
        # Generate visualizations
        radar_config = viz_engine.generate_radar_config(dimension_scores)
        trend_config = viz_engine.generate_trend_chart_config(events)
        network_data = viz_engine.generate_network_visualization(entity)
        insights_html = viz_engine.generate_insights_html(insights)
        patterns_html = viz_engine.generate_patterns_html(patterns)
        
        return jsonify({
            'insights': [
                {
                    'category': insight.category,
                    'title': insight.title,
                    'description': insight.description,
                    'impact': insight.impact,
                    'confidence': insight.confidence,
                    'supporting_evidence': insight.supporting_evidence,
                    'trend': insight.trend
                } for insight in insights
            ],
            'patterns': [
                {
                    'pattern_type': pattern.pattern_type,
                    'description': pattern.description,
                    'frequency': pattern.frequency,
                    'last_occurrence': pattern.last_occurrence.isoformat(),
                    'risk_level': pattern.risk_level,
                    'recommendation': pattern.recommendation
                } for pattern in patterns
            ],
            'confidence_intervals': confidence_intervals,
            'visualizations': {
                'radar_chart': radar_config,
                'trend_chart': trend_config,
                'network_graph': network_data
            },
            'html_components': {
                'insights': insights_html,
                'patterns': patterns_html
            },
            'analytics_summary': {
                'total_insights': len(insights),
                'total_patterns': len(patterns),
                'event_count': len(events),
                'analysis_depth': 'comprehensive'
            }
        })
        
    except Exception as e:
        logging.error(f"Error generating insights for {persona_id}: {str(e)}")
        return jsonify({'error': 'Insights generation failed'}), 500

@app.route('/api/trust/<persona_id>/timeline')
def get_trust_timeline(persona_id):
    """Get detailed timeline analysis for a persona."""
    try:
        entity, events = get_persona_data(persona_id)
        if not entity:
            return jsonify({'error': 'Persona not found'}), 404
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # Create timeline data
        timeline_data = []
        for event in sorted_events:
            timeline_data.append({
                'date': event.timestamp.isoformat(),
                'event_type': event.event_type,
                'description': event.description,
                'outcome': event.outcome,
                'channel': event.channel,
                'impact_score': {
                    'positive': 3,
                    'negative': -2,
                    'neutral': 0
                }.get(event.outcome, 0)
            })
        
        # Calculate rolling trust scores (simplified)
        rolling_scores = []
        for i in range(0, len(sorted_events), max(1, len(sorted_events) // 10)):
            subset_events = sorted_events[:i+1]
            if len(subset_events) >= 3:  # Need minimum events for calculation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                score = loop.run_until_complete(calculate_trust(entity, subset_events))
                loop.close()
                
                rolling_scores.append({
                    'date': subset_events[-1].timestamp.isoformat(),
                    'composite_score': score.composite_score,
                    'chitty_score': score.chitty_score,
                    'event_count': len(subset_events)
                })
        
        return jsonify({
            'timeline': timeline_data,
            'rolling_scores': rolling_scores,
            'summary': {
                'total_events': len(events),
                'date_range': {
                    'start': sorted_events[0].timestamp.isoformat() if sorted_events else None,
                    'end': sorted_events[-1].timestamp.isoformat() if sorted_events else None
                },
                'event_types': list(set(e.event_type for e in events)),
                'outcome_distribution': {
                    'positive': len([e for e in events if e.outcome == 'positive']),
                    'negative': len([e for e in events if e.outcome == 'negative']),
                    'neutral': len([e for e in events if e.outcome == 'neutral'])
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Error generating timeline for {persona_id}: {str(e)}")
        return jsonify({'error': 'Timeline generation failed'}), 500

@app.route('/api/compare')
def compare_personas():
    """Compare trust scores across all personas."""
    try:
        personas = ['alice', 'bob', 'charlie']
        comparison_data = {}
        
        for persona_id in personas:
            entity, events = get_persona_data(persona_id)
            if entity:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                trust_score = loop.run_until_complete(calculate_trust(entity, events))
                loop.close()
                
                comparison_data[persona_id] = {
                    'name': entity.name,
                    'dimensions': {
                        'source': trust_score.source_score,
                        'temporal': trust_score.temporal_score,
                        'channel': trust_score.channel_score,
                        'outcome': trust_score.outcome_score,
                        'network': trust_score.network_score,
                        'justice': trust_score.justice_score
                    },
                    'output_scores': {
                        'people': trust_score.people_score,
                        'legal': trust_score.legal_score,
                        'state': trust_score.state_score,
                        'chitty': trust_score.chitty_score
                    },
                    'composite': trust_score.composite_score,
                    'event_count': len(events),
                    'chitty_level': get_chitty_level(trust_score.composite_score)
                }
        
        return jsonify({
            'comparison': comparison_data,
            'rankings': {
                'by_chitty_score': sorted(
                    comparison_data.items(), 
                    key=lambda x: x[1]['output_scores']['chitty'], 
                    reverse=True
                ),
                'by_composite': sorted(
                    comparison_data.items(),
                    key=lambda x: x[1]['composite'],
                    reverse=True
                )
            }
        })
        
    except Exception as e:
        logging.error(f"Error comparing personas: {str(e)}")
        return jsonify({'error': 'Comparison failed'}), 500

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
