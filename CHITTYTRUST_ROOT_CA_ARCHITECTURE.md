# ChittyTrust Root CA Architecture

## Overview

**chittyfoundation/chittytrust** is the **root-of-trust authority** for the entire ChittyOS ecosystem. It manages cryptographic trust anchors, CA key material, and trust policies that govern the entire federation.

**Distinction from ChittyScore:**
- **ChittyScore** (`chittyscore/`) = Behavioral trust scoring engine (analytical)
- **ChittyTrust** (`chittyfoundation/chittytrust`) = Cryptographic root authority (governance)

---

## Core Responsibilities

### 1. Root Key Management
- Generate and protect root CA private keys (offline storage)
- Intermediate CA key generation and lifecycle
- Hardware Security Module (HSM) integration
- Key rotation policies and procedures
- Emergency revocation capabilities

### 2. Trust Anchor Issuance
- Issue intermediate CA certificates to operational services
- Cross-certification with external PKI systems
- Certificate policy (CP) and certification practice statement (CPS) enforcement
- Trust anchor distribution to ecosystem participants

### 3. Trust Governance
- Define certificate policies for different trust levels
- Approval workflow for certificate issuance requests
- Audit and compliance monitoring
- Policy versioning and migration

### 4. Integration Points
- **chittycert** - Delegates operational certificate issuance
- **chittyregister** - Validates certificates during onboarding
- **chittychain** - Records all trust events immutably
- **chittyscore** - Consumes cert data for behavioral scoring

---

## Architecture Components

### Component Structure

```
chittyfoundation/chittytrust/
├── server/                      # Trust authority service (Node.js/Hono)
│   ├── src/
│   │   ├── index.ts            # Entry point (Cloudflare Worker)
│   │   ├── routes/
│   │   │   ├── root-ca.ts      # Root CA operations (offline)
│   │   │   ├── intermediate.ts # Intermediate CA management
│   │   │   ├── policy.ts       # Trust policy endpoints
│   │   │   └── audit.ts        # Audit and compliance queries
│   │   ├── services/
│   │   │   ├── key-management.ts   # Key generation, storage, rotation
│   │   │   ├── cert-authority.ts   # Certificate signing logic
│   │   │   ├── policy-engine.ts    # Policy validation
│   │   │   └── hsm-interface.ts    # HSM/KMS integration
│   │   ├── lib/
│   │   │   ├── crypto.ts       # Cryptographic primitives
│   │   │   ├── validation.ts   # Certificate validation
│   │   │   └── database.ts     # Neon PostgreSQL client
│   │   └── types/
│   │       ├── certificates.ts # Certificate data structures
│   │       ├── policies.ts     # Policy definitions
│   │       └── audit.ts        # Audit event types
│   ├── wrangler.toml           # Cloudflare deployment config
│   ├── package.json
│   └── tsconfig.json
├── policies/                    # Trust policy documents
│   ├── certificate-policy.md   # CP (RFC 3647 compliant)
│   ├── practice-statement.md   # CPS
│   ├── key-ceremony.md         # Root key generation procedure
│   └── emergency-response.md   # Incident response plan
├── scripts/                     # Operational scripts
│   ├── generate-root-ca.sh     # Root CA creation (offline)
│   ├── issue-intermediate.sh   # Issue intermediate CA cert
│   ├── revoke-certificate.sh   # Emergency revocation
│   └── audit-export.sh         # Export audit logs
├── schema/
│   ├── init-database.sql       # Trust authority database schema
│   └── migrations/             # Schema migrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/               # Security-specific tests
├── docs/
│   ├── API.md                  # API documentation
│   ├── GOVERNANCE.md           # Trust governance model
│   └── INTEGRATION.md          # Integration guide
├── CLAUDE.md                   # Claude Code guidance
├── README.md
└── .github/
    └── workflows/
        ├── security-audit.yml  # Automated security checks
        └── deploy.yml          # Deployment pipeline
```

---

## Database Schema

### Core Tables

```sql
-- Root and Intermediate CA certificates
CREATE TABLE ca_certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type VARCHAR(20) NOT NULL CHECK (type IN ('root', 'intermediate')),
  common_name VARCHAR(255) NOT NULL,
  serial_number VARCHAR(64) UNIQUE NOT NULL,
  public_key_pem TEXT NOT NULL,
  certificate_pem TEXT NOT NULL,
  issuer_id UUID REFERENCES ca_certificates(id),
  valid_from TIMESTAMP NOT NULL,
  valid_until TIMESTAMP NOT NULL,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),
  revocation_reason TEXT,
  revoked_at TIMESTAMP,
  key_algorithm VARCHAR(50) NOT NULL,
  key_size INT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR(255) NOT NULL,
  metadata JSONB
);

-- Certificate policies
CREATE TABLE certificate_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  policy_oid VARCHAR(255) UNIQUE NOT NULL,
  version VARCHAR(20) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  trust_level VARCHAR(20) NOT NULL CHECK (trust_level IN ('L0', 'L1', 'L2', 'L3', 'L4')),
  requirements JSONB NOT NULL,  -- Policy requirements
  constraints JSONB,            -- Technical constraints
  active BOOLEAN DEFAULT true,
  effective_from TIMESTAMP NOT NULL,
  effective_until TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  approved_by VARCHAR(255)
);

-- Certificate issuance requests
CREATE TABLE issuance_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_type VARCHAR(20) NOT NULL CHECK (request_type IN ('intermediate', 'cross_cert', 'renewal')),
  requestor_chittyid VARCHAR(50) NOT NULL,
  requestor_service VARCHAR(50),  -- e.g., 'chittycert', 'chittyauth'
  subject_dn VARCHAR(500) NOT NULL,
  public_key_pem TEXT NOT NULL,
  policy_id UUID REFERENCES certificate_policies(id),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'issued')),
  approval_chain JSONB,  -- Chain of approvals
  issued_cert_id UUID REFERENCES ca_certificates(id),
  created_at TIMESTAMP DEFAULT NOW(),
  approved_at TIMESTAMP,
  issued_at TIMESTAMP,
  metadata JSONB
);

-- Trust anchor distribution
CREATE TABLE trust_anchors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ca_cert_id UUID REFERENCES ca_certificates(id) NOT NULL,
  distribution_format VARCHAR(20) NOT NULL CHECK (distribution_format IN ('pem', 'der', 'p7b', 'jks')),
  anchor_bundle BYTEA NOT NULL,
  version VARCHAR(20) NOT NULL,
  checksum VARCHAR(128) NOT NULL,
  distribution_url TEXT,
  active BOOLEAN DEFAULT true,
  distributed_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

-- Audit log (critical for compliance)
CREATE TABLE trust_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
  actor_chittyid VARCHAR(50),
  actor_service VARCHAR(50),
  target_entity_id UUID,
  target_entity_type VARCHAR(50),
  action VARCHAR(100) NOT NULL,
  result VARCHAR(20) NOT NULL CHECK (result IN ('success', 'failure', 'partial')),
  details JSONB NOT NULL,
  ip_address INET,
  user_agent TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  immutable_hash VARCHAR(128)  -- Hash chained to chittychain
);

-- Cross-certification records
CREATE TABLE cross_certifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  our_ca_id UUID REFERENCES ca_certificates(id) NOT NULL,
  external_ca_name VARCHAR(255) NOT NULL,
  external_ca_cert_pem TEXT NOT NULL,
  cross_cert_pem TEXT NOT NULL,
  trust_direction VARCHAR(20) NOT NULL CHECK (trust_direction IN ('inbound', 'outbound', 'bidirectional')),
  valid_from TIMESTAMP NOT NULL,
  valid_until TIMESTAMP NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  agreement_reference VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

-- Indexes
CREATE INDEX idx_ca_certs_serial ON ca_certificates(serial_number);
CREATE INDEX idx_ca_certs_status ON ca_certificates(status);
CREATE INDEX idx_ca_certs_type ON ca_certificates(type);
CREATE INDEX idx_policies_oid ON certificate_policies(policy_oid);
CREATE INDEX idx_requests_status ON issuance_requests(status);
CREATE INDEX idx_audit_timestamp ON trust_audit_log(timestamp DESC);
CREATE INDEX idx_audit_actor ON trust_audit_log(actor_chittyid);
CREATE INDEX idx_audit_event_type ON trust_audit_log(event_type);
```

---

## API Endpoints

### Root CA Operations (Offline/Admin Only)

```typescript
// POST /api/v1/root-ca/generate
// Generates root CA (offline ceremony, manual approval required)
{
  "common_name": "ChittyOS Root CA G1",
  "country": "US",
  "organization": "ChittyFoundation",
  "validity_years": 20,
  "key_algorithm": "RSA-4096",
  "approved_by": ["DID:CHITTY:FOUNDER_1", "DID:CHITTY:FOUNDER_2"]
}

// POST /api/v1/root-ca/revoke
// Emergency root CA revocation
{
  "ca_id": "uuid",
  "reason": "key_compromise",
  "authorized_by": ["multi-sig required"]
}
```

### Intermediate CA Management

```typescript
// POST /api/v1/intermediate/request
// Request intermediate CA certificate
{
  "service_name": "chittycert",
  "chittyid": "DID:CHITTY:SERVICE_123",
  "subject_dn": "CN=ChittyCert Issuing CA,O=ChittyFoundation",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----...",
  "policy_oid": "1.3.6.1.4.1.XXXXX.1.2.1",
  "validity_years": 5
}

// GET /api/v1/intermediate/{id}
// Retrieve intermediate CA details

// POST /api/v1/intermediate/{id}/renew
// Renew intermediate CA before expiry

// POST /api/v1/intermediate/{id}/revoke
// Revoke intermediate CA
```

### Policy Management

```typescript
// GET /api/v1/policies
// List all certificate policies

// GET /api/v1/policies/{oid}
// Get specific policy details

// POST /api/v1/policies/validate
// Validate issuance request against policy
{
  "policy_oid": "1.3.6.1.4.1.XXXXX.1.2.1",
  "request": { /* issuance request */ }
}
```

### Trust Anchor Distribution

```typescript
// GET /api/v1/trust-anchors
// Get current trust anchor bundle
// Response: PEM bundle of all active root CAs

// GET /api/v1/trust-anchors/version/{version}
// Get specific version of trust anchors

// GET /api/v1/trust-anchors/verify
// Verify integrity of trust anchor bundle
```

### Audit & Compliance

```typescript
// GET /api/v1/audit/events
// Query audit log (with filters)

// GET /api/v1/audit/report
// Generate compliance report

// POST /api/v1/audit/export
// Export audit logs to chittychain
```

---

## Trust Governance Model

### Trust Levels & Certificate Policies

| Level | Name | Use Case | Policy OID | Validation Requirements |
|-------|------|----------|------------|------------------------|
| L0 | Anonymous | Public endpoints | 1.3.6.1.4.1.XXXXX.1.0 | None |
| L1 | Basic | Registered users | 1.3.6.1.4.1.XXXXX.1.1 | ChittyID + email verification |
| L2 | Enhanced | Verified individuals | 1.3.6.1.4.1.XXXXX.1.2 | L1 + identity document |
| L3 | Professional | Organizations | 1.3.6.1.4.1.XXXXX.1.3 | L2 + business registration |
| L4 | Institutional | Critical infrastructure | 1.3.6.1.4.1.XXXXX.1.4 | L3 + audit + compliance |

### Certificate Hierarchy

```
ChittyOS Root CA G1 (RSA-4096, 20 years)
├── ChittyCert Issuing CA (RSA-3072, 5 years)
│   ├── End-entity certificates (RSA-2048, 1-2 years)
│   └── TLS certificates (ECDSA P-256, 90 days)
├── ChittyAuth Token Signing CA (ECDSA P-384, 3 years)
│   └── JWT signing certificates (ECDSA P-256, 1 year)
├── ChittyChain Timestamping CA (RSA-3072, 7 years)
│   └── TSA certificates (RSA-2048, 2 years)
└── Cross-Certification CA (RSA-3072, 5 years)
    └── External PKI bridges
```

### Approval Workflow

**Intermediate CA Issuance:**
1. Service submits request via API
2. Automated policy validation
3. Manual review by Trust Committee (2-of-3 multi-sig)
4. Issuance ceremony (logged to chittychain)
5. Distribution to requesting service
6. Publication to trust anchor repository

**Emergency Revocation:**
1. Incident detection
2. Emergency response team activation
3. Impact assessment
4. Revocation execution (3-of-5 multi-sig)
5. CRL/OCSP update
6. Notification to all relying parties
7. Post-mortem and policy update

---

## Key Management

### Root CA Key (Offline)

- **Generation:** Offline air-gapped ceremony
- **Storage:** Hardware Security Module (HSM) or Cloudflare's KMS
- **Access:** Require 3-of-5 authorized personnel
- **Backup:** Geographically distributed, encrypted
- **Usage:** Only for signing intermediate CAs (annual ceremony)

### Intermediate CA Keys

- **Generation:** Cloudflare Workers KMS
- **Storage:** Cloudflare Durable Objects + R2 backup
- **Access:** Service-specific RBAC
- **Rotation:** Every 3-5 years (before expiry)
- **Revocation:** CRL published hourly, OCSP real-time

### Key Ceremony Procedures

See `policies/key-ceremony.md` for detailed procedures:
1. Pre-ceremony preparation
2. Participant verification
3. Entropy generation
4. Key generation witness
5. Key export and split
6. Certificate signing
7. Verification and distribution
8. Post-ceremony audit

---

## Security Controls

### Authentication & Authorization

- **API Access:** Mutual TLS (mTLS) required for all endpoints
- **Admin Operations:** Multi-signature approval (threshold signatures)
- **Audit Logging:** Every operation logged immutably
- **Rate Limiting:** Strict rate limits on sensitive endpoints

### Cryptographic Standards

- **Algorithms:** RSA-4096 (root), RSA-3072 (intermediate), ECDSA P-384/P-256
- **Hash Functions:** SHA-384 (root), SHA-256 (intermediate and below)
- **Key Storage:** FIPS 140-2 Level 3 compliant
- **Random Number Generation:** Cloudflare's entropy source + drand beacon

### Operational Security

- **Deployment:** Isolated Cloudflare Worker (no shared bindings except database)
- **Monitoring:** Real-time alerts on anomalous activity
- **Backup:** Daily encrypted backups to R2, replicated across regions
- **Disaster Recovery:** Documented procedures, tested quarterly

---

## Integration with ChittyOS Services

### chittycert (Operational Certificate Service)

```typescript
// ChittyCert requests intermediate CA during bootstrap
const intermediateRequest = await fetch('https://trust.chitty.foundation/api/v1/intermediate/request', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${CHITTY_TRUST_SERVICE_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_name: 'chittycert',
    chittyid: await getServiceChittyID(),
    subject_dn: 'CN=ChittyCert Issuing CA,O=ChittyFoundation',
    public_key_pem: generatedPublicKey,
    policy_oid: '1.3.6.1.4.1.XXXXX.1.2.1',
    validity_years: 5
  })
});

// ChittyCert validates certificates against root trust anchor
const trustAnchors = await fetch('https://trust.chitty.foundation/api/v1/trust-anchors');
const isValid = verifyCertificateChain(certificate, trustAnchors);
```

### chittyregister (Compliance Gateway)

```typescript
// ChittyRegister validates service certificates during onboarding
const certDetails = await fetch(`https://trust.chitty.foundation/api/v1/intermediate/${certId}`);

if (certDetails.status !== 'active') {
  throw new Error('Certificate not active or revoked');
}

// Check policy compliance
const policyValidation = await fetch('https://trust.chitty.foundation/api/v1/policies/validate', {
  method: 'POST',
  body: JSON.stringify({
    policy_oid: certDetails.policy_oid,
    request: serviceOnboardingRequest
  })
});
```

### chittychain (Immutable Audit)

```typescript
// ChittyTrust publishes trust events to chittychain
async function publishTrustEvent(event: TrustEvent) {
  // Store in local audit log
  const auditRecord = await db.trust_audit_log.insert(event);

  // Publish to chittychain for immutability
  await fetch('https://chain.chitty.cc/api/v1/events', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${CHITTY_CHAIN_TOKEN}` },
    body: JSON.stringify({
      event_type: 'trust_authority',
      data: auditRecord,
      hash: sha256(auditRecord),
      prev_hash: await getLastChainHash()
    })
  });
}
```

### chittyscore (Behavioral Trust Scoring)

```typescript
// ChittyScore consumes certificate data for trust scoring
const certProfile = await fetch(`https://trust.chitty.foundation/api/v1/intermediate/${chittyid}`);

// Factor certificate validity into Source Dimension
const sourceTrustBoost = certProfile.trust_level === 'L4' ? 15 :
                         certProfile.trust_level === 'L3' ? 10 :
                         certProfile.trust_level === 'L2' ? 5 : 0;

// Combine with behavioral scoring
const finalScore = behavioralTrustScore + sourceTrustBoost;
```

---

## Deployment

### Cloudflare Workers Configuration

```toml
# wrangler.toml
name = "chittytrust-authority"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[env.production.vars]
ENVIRONMENT = "production"
API_BASE_URL = "https://trust.chitty.foundation"

[[env.production.kv_namespaces]]
binding = "CERT_CACHE"
id = "chittytrust_cert_cache_prod"

[[env.production.d1_databases]]
binding = "TRUST_DB"
database_name = "chittytrust-production"
database_id = "placeholder-production-db-id"

[[env.production.r2_buckets]]
binding = "KEY_STORE"
bucket_name = "chittytrust-keys-prod"
preview_bucket_name = "chittytrust-keys-preview"

[env.production]
routes = [
  { pattern = "trust.chitty.foundation/*", zone_name = "chitty.foundation" }
]
```

### Environment Variables (Secrets)

```bash
wrangler secret put NEON_DATABASE_URL          # PostgreSQL connection
wrangler secret put ROOT_CA_KEY_ID             # KMS key ID for root CA
wrangler secret put INTERMEDIATE_CA_KEY_ID     # KMS key ID for intermediates
wrangler secret put TRUST_ADMIN_API_TOKEN      # Admin API access
wrangler secret put AUDIT_SIGNING_KEY          # Sign audit logs
wrangler secret put CHITTY_CHAIN_SERVICE_TOKEN # Publish to chittychain
```

---

## Governance & Compliance

### Trust Committee

**Composition:**
- 5 members (2-of-3 quorum for intermediate CA, 3-of-5 for root CA operations)
- Roles: ChittyFoundation Board, Technical Leads, External Security Auditor

**Responsibilities:**
- Approve/reject intermediate CA requests
- Review and update certificate policies
- Incident response and emergency revocations
- Quarterly security audits
- Annual root CA key ceremony

### Compliance Requirements

- **WebTrust Principles:** Align with WebTrust for CAs
- **ETSI EN 319 411:** European trust service provider standards
- **SOC 2 Type II:** Annual audit for security and availability
- **ISO 27001:** Information security management
- **Audit Logs:** 7-year retention, immutable storage on chittychain

### Policy Documents

1. **Certificate Policy (CP)** - `policies/certificate-policy.md`
2. **Certification Practice Statement (CPS)** - `policies/practice-statement.md`
3. **Key Ceremony Procedures** - `policies/key-ceremony.md`
4. **Emergency Response Plan** - `policies/emergency-response.md`

---

## Future Roadmap

### Phase 1: Foundation (Q1 2025)
- ✅ Architecture design
- ⏳ Database schema implementation
- ⏳ Root CA generation ceremony
- ⏳ Basic API endpoints

### Phase 2: Operational (Q2 2025)
- ⏳ Intermediate CA issuance workflow
- ⏳ Integration with chittycert
- ⏳ Trust anchor distribution
- ⏳ Audit logging to chittychain

### Phase 3: Compliance (Q3 2025)
- ⏳ WebTrust audit preparation
- ⏳ SOC 2 Type II audit
- ⏳ Cross-certification with external PKIs
- ⏳ Public trust anchor repository

### Phase 4: Advanced Features (Q4 2025)
- ⏳ Quantum-resistant cryptography pilot
- ⏳ Decentralized key ceremony (threshold cryptography)
- ⏳ AI-powered anomaly detection
- ⏳ Zero-knowledge proof integrations

---

## Key URLs

- **Trust Authority:** https://trust.chitty.foundation
- **Trust Anchor Repository:** https://trust.chitty.foundation/anchors
- **CRL Distribution:** https://crl.chitty.foundation
- **OCSP Responder:** https://ocsp.chitty.foundation
- **Policy Documents:** https://trust.chitty.foundation/policies

---

## References

- RFC 5280: Internet X.509 Public Key Infrastructure Certificate and CRL Profile
- RFC 3647: Certificate Policy and Certification Practices Framework
- RFC 6960: Online Certificate Status Protocol (OCSP)
- WebTrust Principles and Criteria for Certification Authorities
- NIST SP 800-57: Recommendation for Key Management
