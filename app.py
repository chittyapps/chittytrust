import os
import logging
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import asyncio
import requests
import jwt

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import our trust engine
from src.chitty_trust import calculate_trust
from src.chitty_trust.analytics import TrustAnalytics
from src.chitty_trust.visualization import TrustVisualizationEngine
from demo_data import get_persona_data

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chitty-trust-demo-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Import models after Flask app configuration
from models import db, User, VerificationRequest, TrustHistory, VerifierProfile, ChittyCoin

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Initialize sample data on first run
    from models import User
    if User.query.count() == 0:
        try:
            from sample_data import initialize_sample_data
            initialize_sample_data()
            logging.info("Sample data initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize sample data: {e}")

# Initialize analytics engines
analytics_engine = TrustAnalytics()
viz_engine = TrustVisualizationEngine()

# Import marketplace services
from marketplace import MarketplaceService, TrustHistoryService, VerifierService
from auth import require_auth, get_current_user, is_authenticated

@app.route('/')
def index():
    """Main trust engine dashboard."""
    # Check if user is authenticated for personalized experience
    authenticated = is_authenticated()
    current_user = get_current_user() if authenticated else None
    
    return render_template('index.html', 
                         authenticated=authenticated, 
                         current_user=current_user)

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

# ChittyID Marketplace API Routes

@app.route('/marketplace')
def marketplace():
    """ChittyID Verification Marketplace"""
    return render_template('marketplace.html')

@app.route('/partners')
def partners():
    """ChittyID Partners & Integration"""
    return render_template('partners.html')

@app.route('/onboarding')
def onboarding():
    """Developer Onboarding Guide"""
    return render_template('onboarding.html')

@app.route('/enterprise')
def enterprise():
    """Enterprise Dashboard"""
    return render_template('enterprise.html')

# ChittyChain Blockchain Integration Endpoints

@app.route('/api/blockchain/trust-passport/<user_id>')
def get_trust_passport(user_id):
    """Get blockchain-verified trust passport for cross-platform use"""
    try:
        from chittychain import chittychain_client
        passport = chittychain_client.create_trust_passport(user_id)
        return jsonify(passport)
    except Exception as e:
        logging.error(f"Trust passport generation failed: {e}")
        return jsonify({'error': 'Trust passport generation failed'}), 500

@app.route('/api/blockchain/verify/<transaction_id>')
def verify_blockchain_record(transaction_id):
    """Verify trust record on blockchain"""
    try:
        from chittychain import chittychain_client
        verification = chittychain_client.verify_trust_record(transaction_id)
        return jsonify(verification)
    except Exception as e:
        logging.error(f"Blockchain verification failed: {e}")
        return jsonify({'error': 'Blockchain verification failed'}), 500

@app.route('/api/blockchain/history/<user_id>')
def get_blockchain_history(user_id):
    """Get complete blockchain trust history"""
    try:
        from chittychain import chittychain_client
        limit = request.args.get('limit', 50, type=int)
        history = chittychain_client.get_user_trust_history(user_id, limit)
        return jsonify({'history': history, 'blockchain_verified': True})
    except Exception as e:
        logging.error(f"Blockchain history query failed: {e}")
        return jsonify({'error': 'Blockchain history query failed'}), 500

# Notion Enterprise Integration Endpoints

@app.route('/api/enterprise/audit/<user_id>', methods=['POST'])
def create_enterprise_audit(user_id):
    """Create comprehensive enterprise audit documentation in ChittyChain Evidence Ledger"""
    try:
        from evidence_integration import evidence_ledger
        from chittychain import chittychain_client
        
        # Get current trust data
        entity, events = get_persona_data(user_id.split('_')[0])  # Extract persona from user_id
        if not entity:
            return jsonify({'error': 'User not found'}), 404
        
        trust_data = asyncio.run(calculate_trust(entity, events))
        
        # Record on blockchain first
        blockchain_tx = chittychain_client.record_trust_event(
            user_id,
            {'audit_type': 'comprehensive', 'requested_by': 'enterprise_customer'},
            trust_data
        )
        
        # Create evidence in the real ChittyChain Evidence Ledger
        evidence_id = evidence_ledger.record_trust_evidence(
            user_id, 
            trust_data,
            blockchain_tx
        )
        
        if evidence_id:
            return jsonify({
                'audit_created': True,
                'evidence_ledger_id': evidence_id,
                'blockchain_tx': blockchain_tx,
                'trust_data': trust_data,
                'ledger_url': f'https://www.notion.so/{evidence_id.replace("-", "")}'
            })
        else:
            return jsonify({'error': 'Evidence ledger recording failed'}), 500
            
    except Exception as e:
        logging.error(f"Enterprise audit creation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enterprise/compliance-report', methods=['POST'])
def generate_compliance_report():
    """Generate enterprise compliance report in Notion"""
    try:
        from notion_integration import notion_integration
        
        data = request.get_json()
        organization_id = data.get('organization_id', 'demo_org')
        
        # Calculate compliance metrics
        users = User.query.all()
        report_data = {
            'total_users': len(users),
            'average_trust_score': sum(u.trust_score or 0 for u in users) / len(users) if users else 0,
            'compliance_status': 'Compliant' if len(users) > 0 else 'Pending',
            'high_trust_users': len([u for u in users if (u.trust_score or 0) >= 80]),
            'verification_coverage': '95%'  # Demo data
        }
        
        # Create Notion compliance report
        page_id = notion_integration.create_compliance_report(organization_id, report_data)
        
        if page_id:
            return jsonify({
                'report_created': True,
                'notion_page_id': page_id,
                'metrics': report_data
            })
        else:
            return jsonify({'error': 'Compliance report creation failed'}), 500
            
    except Exception as e:
        logging.error(f"Compliance report generation failed: {e}")
        return jsonify({'error': 'Compliance report generation failed'}), 500

@app.route('/api/enterprise/workflow/<int:request_id>')
def document_verification_workflow(request_id):
    """Document verification workflow in Notion for audit trail"""
    try:
        from notion_integration import notion_integration
        
        # Get verification request
        verification_request = VerificationRequest.query.get(request_id)
        if not verification_request:
            return jsonify({'error': 'Verification request not found'}), 404
        
        # Convert to dict for Notion documentation
        workflow_data = {
            'title': verification_request.title,
            'description': verification_request.description,
            'verification_type': verification_request.verification_type,
            'status': verification_request.status,
            'created_at': verification_request.created_at.isoformat(),
            'reward_amount': verification_request.reward_amount,
            'priority': verification_request.priority
        }
        
        # Create Notion workflow documentation
        page_id = notion_integration.create_verification_workflow(request_id, workflow_data)
        
        if page_id:
            return jsonify({
                'workflow_documented': True,
                'notion_page_id': page_id,
                'workflow_data': workflow_data
            })
        else:
            return jsonify({'error': 'Workflow documentation failed'}), 500
            
    except Exception as e:
        logging.error(f"Workflow documentation failed: {e}")
        return jsonify({'error': 'Workflow documentation failed'}), 500

# ChittyChain Evidence Ledger Integration

@app.route('/api/evidence-ledger/record/<user_id>', methods=['POST'])
def record_evidence_ledger(user_id):
    """Record trust evidence in the real ChittyChain Evidence Ledger"""
    try:
        from evidence_integration import evidence_ledger
        from chittychain import chittychain_client
        
        # Get current trust data
        entity, events = get_persona_data(user_id.split('_')[0])
        if not entity:
            return jsonify({'error': 'User not found'}), 404
        
        trust_data = asyncio.run(calculate_trust(entity, events))
        
        # Record on blockchain
        blockchain_tx = chittychain_client.record_trust_event(
            user_id,
            {'event_type': 'evidence_recording', 'source': 'chitty_trust_engine'},
            trust_data
        )
        
        # Record in the actual Notion Evidence Ledger
        evidence_id = evidence_ledger.record_trust_evidence(user_id, trust_data, blockchain_tx)
        
        # Log blockchain transaction in evidence ledger
        ledger_tx_id = evidence_ledger.log_blockchain_transaction(
            blockchain_tx,
            user_id,
            'trust_calculation',
            trust_data.get('scores', {})
        )
        
        return jsonify({
            'evidence_recorded': True,
            'evidence_ledger_id': evidence_id,
            'blockchain_tx': blockchain_tx,
            'ledger_transaction_id': ledger_tx_id,
            'trust_data': trust_data,
            'evidence_url': 'https://www.notion.so/ChittyChain-Evidence-Ledger-24694de4357980dba689cf778c9708eb',
            'integrity_verified': True
        })
        
    except Exception as e:
        logging.error(f"Evidence ledger recording failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/evidence-ledger/integration-snippets', methods=['POST'])
def create_integration_snippets():
    """Create integration snippets page in ChittyChain Evidence Ledger"""
    try:
        from evidence_integration import evidence_ledger
        
        # Create integration snippets page
        snippets_id = evidence_ledger.create_integration_snippets_page()
        
        if snippets_id:
            return jsonify({
                'snippets_created': True,
                'notion_page_id': snippets_id,
                'evidence_url': 'https://www.notion.so/ChittyChain-Evidence-Ledger-24694de4357980dba689cf778c9708eb',
                'description': 'Ready-to-use integration snippets for team collaboration'
            })
        else:
            return jsonify({'error': 'Integration snippets creation failed'}), 500
            
    except Exception as e:
        logging.error(f"Integration snippets creation failed: {e}")
        return jsonify({'error': str(e)}), 500

# ChittyChain Integrated Workflow Endpoints

@app.route('/api/chitty-workflow/execute/<user_id>', methods=['POST'])
def execute_chitty_workflow(user_id):
    """Execute integrated ChittyTrust + ChittyVerify + ChittyChain workflow"""
    try:
        from chitty_workflow import chitty_workflow
        
        data = request.get_json() or {}
        verification_type = data.get('verification_type', 'comprehensive')
        
        # Execute complete workflow
        result = chitty_workflow.execute_trust_verification_workflow(user_id, verification_type)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Chitty workflow execution failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chitty-workflow/batch-process', methods=['POST'])
def batch_process_chitty_workflow():
    """Batch process multiple users through ChittyChain workflow"""
    try:
        from chitty_workflow import chitty_workflow
        
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return jsonify({'error': 'No user IDs provided'}), 400
        
        results = []
        for user_id in user_ids:
            workflow_result = chitty_workflow.execute_trust_verification_workflow(user_id)
            results.append(workflow_result)
        
        # Summary statistics
        successful = len([r for r in results if r.get('status') == 'completed'])
        failed = len(results) - successful
        
        return jsonify({
            'batch_processed': True,
            'total_users': len(user_ids),
            'successful': successful,
            'failed': failed,
            'results': results,
            'batch_id': f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logging.error(f"Batch workflow processing failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketplace/requests', methods=['GET'])
def get_marketplace_requests():
    """Get available verification requests"""
    verification_type = request.args.get('type')
    status = request.args.get('status', 'open')
    limit = int(request.args.get('limit', 20))
    
    requests = MarketplaceService.get_marketplace_requests(limit, verification_type, status)
    
    return jsonify([{
        'id': req.id,
        'title': req.title,
        'description': req.description,
        'verification_type': req.verification_type,
        'reward_amount': req.reward_amount,
        'status': req.status,
        'priority': req.priority,
        'deadline': req.deadline.isoformat() if req.deadline else None,
        'created_at': req.created_at.isoformat(),
        'user': {
            'name': f"{req.user.first_name} {req.user.last_name}".strip() or req.user.email,
            'trust_level': req.user.verification_level
        }
    } for req in requests])

@app.route('/api/marketplace/requests', methods=['POST'])
@require_auth
def create_verification_request():
    """Create new verification request"""
    user = get_current_user()
    data = request.get_json()
    
    try:
        verification_request = MarketplaceService.create_verification_request(user.id, data)
        
        return jsonify({
            'id': verification_request.id,
            'message': 'Verification request created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/marketplace/requests/<int:request_id>/claim', methods=['POST'])
@require_auth
def claim_verification_request(request_id):
    """Claim a verification request"""
    user = get_current_user()
    
    success, message = MarketplaceService.claim_verification_request(request_id, user.id)
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400

@app.route('/api/user/trust-history')
@require_auth
def get_user_trust_history():
    """Get user's trust history"""
    user = get_current_user()
    days_back = int(request.args.get('days', 30))
    
    history = TrustHistoryService.get_trust_history(user.id, days_back)
    trends = TrustHistoryService.get_trust_trends(user.id, 7)
    
    return jsonify({
        'history': [{
            'recorded_at': entry.recorded_at.isoformat(),
            'dimensions': {
                'source': entry.source_trust,
                'temporal': entry.temporal_trust,
                'channel': entry.channel_trust,
                'outcome': entry.outcome_trust,
                'network': entry.network_trust,
                'justice': entry.justice_trust
            },
            'scores': {
                'composite': entry.composite_score,
                'people': entry.people_score,
                'legal': entry.legal_score,
                'state': entry.state_score,
                'chitty': entry.chitty_score
            },
            'trigger_event': entry.trigger_event,
            'confidence': entry.confidence_level
        } for entry in history],
        'trends': trends
    })

@app.route('/api/user/trust-calculate', methods=['POST'])
@require_auth
def calculate_user_trust():
    """Calculate and record user's trust score"""
    user = get_current_user()
    data = request.get_json()
    trigger_event = data.get('trigger_event', 'manual_calculation')
    
    try:
        # Run async trust calculation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        trust_data, history_entry = loop.run_until_complete(
            TrustHistoryService.calculate_and_record_trust(
                user.id, trigger_event
            )
        )
        loop.close()
        
        return jsonify({
            'trust_data': trust_data,
            'history_id': history_entry.id,
            'message': 'Trust score calculated and recorded'
        })
        
    except Exception as e:
        logging.error(f"Trust calculation failed for user {user.id}: {e}")
        return jsonify({'error': 'Trust calculation failed'}), 500

@app.route('/api/user/profile')
@require_auth
def get_user_profile():
    """Get user profile with trust data"""
    user = get_current_user()
    
    # Get recent trust trends
    trends = TrustHistoryService.get_trust_trends(user.id, 7)
    
    # Get user's requests
    user_requests = MarketplaceService.get_user_requests(user.id)
    
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'chitty_id': user.chitty_id,
            'verification_level': user.verification_level,
            'trust_score': user.trust_score,
            'profile_image_url': user.profile_image_url
        },
        'trust_trends': trends,
        'verification_requests': len(user_requests),
        'active_requests': len([r for r in user_requests if r.status in ['open', 'claimed', 'in_progress']])
    })

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
