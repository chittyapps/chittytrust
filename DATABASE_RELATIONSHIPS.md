# ChittyScore Database Relationships

## Key Concept: UUID vs ChittyID

### identities Table (Owned by ChittyID)
```sql
CREATE TABLE identities (
    id UUID PRIMARY KEY,           -- Internal database ID (random UUID)
    did VARCHAR UNIQUE NOT NULL,   -- ChittyID (e.g., "01-C-ACT-AB12-P-2511-3-X")
    biometric_hash TEXT,
    public_key TEXT,
    status VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Example Record:**
```
id:   "550e8400-e29b-41d4-a716-446655440000"  ← UUID (internal DB)
did:  "01-C-ACT-1234-P-2511-A-X"              ← ChittyID (human-readable)
```

---

## ChittyScore Tables Reference identities.id (UUID)

### trust_scores Table
```sql
CREATE TABLE trust_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Trust score record ID
    identity_id UUID NOT NULL,                      -- → identities.id (UUID)
    composite_score NUMERIC(5,2),
    -- ... 6D scores
);
```

### trust_events Table
```sql
CREATE TABLE trust_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Event record ID
    identity_id UUID NOT NULL,                      -- → identities.id (UUID)
    event_type VARCHAR(50),
    -- ... event data
);
```

---

## Why UUIDs, Not ChittyIDs Directly?

### ✅ Correct: Use UUIDs for Foreign Keys
```sql
-- Foreign key relationship
ALTER TABLE trust_scores
    ADD CONSTRAINT fk_trust_scores_identity
    FOREIGN KEY (identity_id) REFERENCES identities(id);
```

**Reasons:**
1. **Database efficiency** - UUID joins are faster than string (ChittyID) joins
2. **Referential integrity** - Database can enforce foreign keys
3. **Standard practice** - Internal IDs separate from human-readable identifiers
4. **ChittyID changes** - If ChittyID format changes, internal references remain stable

### ❌ Incorrect: Storing ChittyID directly
```sql
-- DON'T DO THIS
CREATE TABLE trust_scores (
    chitty_id VARCHAR NOT NULL  -- ❌ String join, no FK constraint
);
```

---

## Lookup Flow

### From ChittyID to Trust Score:
```sql
-- User provides ChittyID: "01-C-ACT-1234-P-2511-A-X"
-- Lookup internal UUID first:
SELECT id FROM identities WHERE did = '01-C-ACT-1234-P-2511-A-X';
-- Returns: "550e8400-e29b-41d4-a716-446655440000"

-- Then get trust scores:
SELECT * FROM trust_scores
WHERE identity_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY calculated_at DESC
LIMIT 1;
```

### From UUID to ChittyID:
```sql
-- Join to get human-readable ChittyID in results:
SELECT
    ts.*,
    i.did as chitty_id,
    i.status as identity_status
FROM trust_scores ts
JOIN identities i ON ts.identity_id = i.id
WHERE ts.identity_id = '550e8400-e29b-41d4-a716-446655440000';
```

---

## API Usage

### Calculate Trust Score (Input: ChittyID)
```python
@app.route('/api/trust/calculate', methods=['POST'])
def calculate_trust():
    data = request.get_json()
    chitty_id = data['chitty_id']  # "01-C-ACT-1234-P-2511-A-X"

    # Step 1: Lookup internal UUID
    identity = db.query(
        "SELECT id, did FROM identities WHERE did = %s",
        [chitty_id]
    ).fetchone()

    if not identity:
        return {"error": "ChittyID not found"}, 404

    identity_uuid = identity['id']  # UUID

    # Step 2: Calculate trust score
    trust_score = calculate_6d_trust(identity_uuid)

    # Step 3: Save to database
    db.execute(
        """INSERT INTO trust_scores
           (identity_id, composite_score, ...)
           VALUES (%s, %s, ...)""",
        [identity_uuid, trust_score, ...]
    )

    # Step 4: Return result with ChittyID
    return {
        "chitty_id": chitty_id,          # Human-readable
        "identity_id": identity_uuid,    # Internal UUID
        "trust_score": trust_score
    }
```

---

## Summary

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `identities.id` | UUID | Internal DB primary key | `550e8400-e29b-41d4-a716-446655440000` |
| `identities.did` | VARCHAR | ChittyID (human-readable) | `01-C-ACT-1234-P-2511-A-X` |
| `trust_scores.id` | UUID | Trust score record ID | `7c9e6679-7425-40de-944b-e07fc1f90ae7` |
| `trust_scores.identity_id` | UUID | Foreign key to `identities.id` | `550e8400-e29b-41d4-a716-446655440000` |

**Key Point:** Always use `identities.id` (UUID) for foreign keys, not `identities.did` (ChittyID string).
