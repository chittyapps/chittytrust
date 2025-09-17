-- ChittyTrust D1 Database Schema
-- Court-admissible trust scoring and evidence tracking

-- Trust scores history table
CREATE TABLE IF NOT EXISTS trust_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id TEXT NOT NULL,
    composite_score REAL NOT NULL,
    people_score REAL NOT NULL,
    legal_score REAL NOT NULL,
    state_score REAL NOT NULL,
    chitty_score REAL NOT NULL,
    source_dimension REAL NOT NULL,
    temporal_dimension REAL NOT NULL,
    channel_dimension REAL NOT NULL,
    outcome_dimension REAL NOT NULL,
    network_dimension REAL NOT NULL,
    justice_dimension REAL NOT NULL,
    confidence REAL NOT NULL,
    ai_enhanced BOOLEAN DEFAULT TRUE,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON metadata
);

-- Evidence records table
CREATE TABLE IF NOT EXISTS evidence_records (
    id TEXT PRIMARY KEY, -- Evidence ID
    persona_id TEXT,
    file_hash TEXT NOT NULL,
    blockchain_hash TEXT NOT NULL,
    blockchain_block INTEGER NOT NULL,
    storage_key TEXT NOT NULL,
    content_type TEXT,
    file_size INTEGER,
    verification_status TEXT DEFAULT 'verified',
    authenticity_score REAL DEFAULT 1.0,
    chain_of_custody_id TEXT,
    legal_admissible BOOLEAN DEFAULT TRUE,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON metadata
);

-- Verification requests (marketplace)
CREATE TABLE IF NOT EXISTS verification_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,
    persona_id TEXT,
    reward_amount INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',
    claimed_by TEXT,
    completed_at DATETIME,
    ai_assisted BOOLEAN DEFAULT TRUE,
    evidence_required BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON metadata
);

-- Trust timeline events
CREATE TABLE IF NOT EXISTS trust_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_description TEXT,
    impact_score REAL DEFAULT 0,
    evidence_id TEXT,
    verification_id INTEGER,
    ai_detected BOOLEAN DEFAULT FALSE,
    occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON metadata
);

-- AI insights and recommendations
CREATE TABLE IF NOT EXISTS ai_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    category TEXT,
    title TEXT,
    description TEXT,
    confidence REAL NOT NULL,
    ai_model TEXT,
    recommendations TEXT, -- JSON array
    patterns TEXT, -- JSON array
    expires_at DATETIME,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    client_ip TEXT,
    user_agent TEXT,
    api_key_hash TEXT,
    country TEXT,
    ray_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trust_scores_persona_id ON trust_scores(persona_id);
CREATE INDEX IF NOT EXISTS idx_trust_scores_calculated_at ON trust_scores(calculated_at);
CREATE INDEX IF NOT EXISTS idx_evidence_records_persona_id ON evidence_records(persona_id);
CREATE INDEX IF NOT EXISTS idx_evidence_records_uploaded_at ON evidence_records(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_verification_requests_status ON verification_requests(status);
CREATE INDEX IF NOT EXISTS idx_trust_events_persona_id ON trust_events(persona_id);
CREATE INDEX IF NOT EXISTS idx_trust_events_occurred_at ON trust_events(occurred_at);
CREATE INDEX IF NOT EXISTS idx_ai_insights_persona_id ON ai_insights(persona_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp);

-- Insert sample data for demo personas
INSERT OR IGNORE INTO trust_scores (
    persona_id, composite_score, people_score, legal_score, state_score, chitty_score,
    source_dimension, temporal_dimension, channel_dimension, outcome_dimension, network_dimension, justice_dimension,
    confidence, metadata
) VALUES 
('alice', 88.5, 92.0, 85.0, 90.0, 87.5, 85, 80, 75, 95, 88, 92, 0.95, '{"demo": true, "ai_enhanced": true}'),
('bob', 72.3, 68.0, 78.0, 70.0, 75.0, 70, 75, 68, 85, 65, 70, 0.82, '{"demo": true, "ai_enhanced": true}'),
('charlie', 45.8, 52.0, 38.0, 48.0, 50.0, 40, 55, 45, 60, 45, 48, 0.78, '{"demo": true, "ai_enhanced": true}');

-- Insert sample evidence records
INSERT OR IGNORE INTO evidence_records (
    id, persona_id, file_hash, blockchain_hash, blockchain_block, storage_key,
    content_type, file_size, verification_status, authenticity_score, chain_of_custody_id,
    metadata
) VALUES 
('EVD-ALICE-001', 'alice', 'a1b2c3d4e5f6789012345678901234567890abcd', 'blockchain_hash_001', 750123, 'evidence/EVD-ALICE-001',
 'application/pdf', 524288, 'verified', 0.98, 'COC-EVD-ALICE-001', 
 '{"title": "Community Leadership Certificate", "court_admissible": true}'),
('EVD-BOB-001', 'bob', 'b2c3d4e5f6a78901234567890123456789abcdef', 'blockchain_hash_002', 750124, 'evidence/EVD-BOB-001',
 'image/jpeg', 1048576, 'verified', 0.85, 'COC-EVD-BOB-001',
 '{"title": "Business License Photo", "court_admissible": true}');

-- Insert sample verification requests
INSERT OR IGNORE INTO verification_requests (
    title, description, type, persona_id, reward_amount, status, ai_assisted, evidence_required, metadata
) VALUES 
('AI-Enhanced Identity Verification', 'Verify identity using advanced AI analysis', 'identity', 'alice', 100, 'open', TRUE, TRUE, 
 '{"ai_models": ["fraud-detection", "sentiment"], "priority": "high"}'),
('Business Credential Verification', 'Verify business credentials and track record', 'business', 'bob', 150, 'open', TRUE, TRUE,
 '{"ai_models": ["trust-insights"], "priority": "medium"}'),
('Community Impact Assessment', 'Assess community involvement and impact', 'community', 'charlie', 75, 'open', TRUE, FALSE,
 '{"ai_models": ["sentiment", "trust-insights"], "priority": "low"}');

-- Insert sample trust events
INSERT OR IGNORE INTO trust_events (
    persona_id, event_type, event_description, impact_score, ai_detected, metadata
) VALUES 
('alice', 'verification', 'Identity verified with blockchain evidence', 5.0, TRUE, '{"evidence_type": "identity", "ai_confidence": 0.95}'),
('alice', 'outcome', 'Successfully completed community project', 3.0, FALSE, '{"project_type": "community_service"}'),
('bob', 'verification', 'Business license verified', 4.0, TRUE, '{"evidence_type": "business", "ai_confidence": 0.82}'),
('bob', 'dispute', 'Minor customer complaint resolved', -1.0, TRUE, '{"resolution": "successful", "ai_detected_resolution": true}'),
('charlie', 'improvement', 'Completed rehabilitation program', 8.0, FALSE, '{"program_type": "rehabilitation", "transformation": true}');

-- Insert sample AI insights
INSERT OR IGNORE INTO ai_insights (
    persona_id, insight_type, category, title, description, confidence, ai_model, recommendations, patterns
) VALUES 
('alice', 'strength', 'leadership', 'Strong Community Leadership', 
 'Demonstrates consistent leadership qualities and community engagement', 0.92, '@cf/meta/llama-2-7b-chat-int8',
 '["Continue community involvement", "Consider mentoring others"]', '["consistent_positive_outcomes", "strong_network_connections"]'),
('bob', 'vulnerability', 'communication', 'Mixed Customer Relations',
 'Shows room for improvement in customer communication and satisfaction', 0.78, '@cf/meta/llama-2-7b-chat-int8',
 '["Improve customer service training", "Implement feedback system"]', '["occasional_disputes", "business_focus"]'),
('charlie', 'opportunity', 'transformation', 'Positive Transformation Trajectory',
 'Shows strong commitment to personal improvement and positive change', 0.85, '@cf/meta/llama-2-7b-chat-int8',
 '["Continue current improvement path", "Seek additional mentorship"]', '["transformation_pattern", "increasing_trust_scores"]');