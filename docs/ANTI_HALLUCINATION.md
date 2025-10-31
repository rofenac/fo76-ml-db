# Anti-Hallucination Controls

## Critical Limitation

**LLM hallucination cannot be 100% prevented.** Large language models are probabilistic systems that generate text based on patterns, not deterministic databases. Training data is "baked into" model weights and cannot be removed.

**Goal:** Implement multiple layers of controls to **significantly reduce** hallucination risk.

---

## Implemented Controls

### 1. Strict System Prompts

**Location:**
- `rag/query_engine.py` (SQL mode, lines 257-286)
- `rag/hybrid_query_engine.py` (Vector mode, lines 561-585)

**Key directives:**
```python
system="""You are a database results formatter. You have ZERO knowledge...

⚠️ CRITICAL: You are STRICTLY FORBIDDEN from using your training data...

ABSOLUTE RULES:
1. ONLY use data from database results
2. NEVER mention items not in results
3. NEVER speculate about what "might exist"
4. If data is missing, say "not available in database"
"""
```

**Limitations:** LLMs don't have perfect instruction following and may still occasionally leak training knowledge.

### 2. Low Temperature Setting

**Implementation:** `temperature=0.3` in both query engines

**Effect:**
- More deterministic, conservative responses
- Reduces creative outputs that might hallucinate
- Favors high-probability tokens

**Tradeoffs:**
- Lower temperature = less hallucination, but more robotic responses
- Temperature 0.0 = maximum determinism but too repetitive
- Temperature 1.0+ = creative but high hallucination risk

### 3. Database-Only Context

**Effect:** LLM only receives database results, no external information

**Limitations:** Training data remains in model weights and can unconsciously blend with database results

### 4. Explicit Violation Examples

**Implementation:**
```
VIOLATION EXAMPLES (DO NOT DO THIS):
❌ "Other perks like Expert Shotgunner might help"
❌ "You should also consider..."
❌ "Players typically use..."
```

**Effect:** Shows LLM concrete forbidden behaviors

**Limitations:** Cannot cover all possible violation patterns

### 5. Conversation History Management

**Implementation:** Last 3 exchanges kept in context

**Effect:** Maintains consistency, prevents contradictions

**Limitations:** Long conversations may drift; history can compound early errors

---

## What We CANNOT Do

1. **100% Prevention** - LLMs are fundamentally probabilistic
2. **Real-time Fact Checking** - Complex statements blend facts subtly; computational cost prohibitive
3. **Model Surgery** - Cannot remove specific knowledge from model weights
4. **Deterministic Outputs** - Even at temp=0.0, token selection remains probabilistic

---

## User Best Practices

### ✅ Do This:

1. **Verify critical information** against database
2. **Use exact queries** (SQL mode) for factual lookups
3. **Watch for red flags:**
   - Words like "typically", "usually", "often" = possible training data leak
   - Items mentioned that weren't in query results
   - Stats inconsistent with database
4. **Run validation tests:** `python rag/test_no_hallucination.py`

### ❌ Don't Do This:

1. Assume 100% accuracy
2. Rely solely on LLM for mission-critical data
3. Ignore validation tests

---

## Testing for Hallucination

### Automated Tests

**Location:** `rag/test_no_hallucination.py`

**Tests:**
- Non-existent items ("Plasma Disruptor")
- Fake perk comparisons
- Verifies LLM says "not in database" instead of inventing data

**Run:**
```bash
cd rag
python test_no_hallucination.py
```

### Manual Test Queries

```
1. "What's the damage of the Plasma Disruptor?"
   → Should say: not in database (fake weapon)

2. "Compare Bloodied Fixer to Nuclear Dragon"
   → Should only discuss Fixer (Nuclear Dragon is fake)

3. "Best perks for the Vaporizer weapon"
   → Should say: no data available (fake weapon)
```

---

## Technical Tradeoffs

**Current Settings (Strict):**
- ✅ Less hallucination, more trustworthy
- ❌ May miss useful inferences, feels cautious

**Alternative (Less Strict):**
- ✅ More creative connections, better language
- ❌ Higher hallucination risk, less trustworthy

**Why we can't go stricter:**
- Temperature < 0.3 = too repetitive, refuses valid questions
- Full validation = parse every statement, match against DB (complex + expensive)

---

## Potential Future Improvements

### 1. Structured Output Validation
Force JSON responses with source attribution:
```json
{
  "items": [{"name": "Gauss Shotgun", "damage": 65, "source": "database"}],
  "disclaimer": "All data from query #1234"
}
```
**Pros:** Easier validation
**Cons:** Less natural

### 2. Two-Pass Verification
Generate answer → validate against DB → return if validated
**Pros:** Catches many hallucinations
**Cons:** 2x cost, 2x latency

### 3. Fact Extraction + Validation
Extract claims → verify with SQL → reject if mismatch
**Pros:** High precision
**Cons:** Complex, expensive, may reject good answers

---

## Summary

**Implemented ✅**
1. Strict system prompts with explicit rules
2. Low temperature (0.3) for determinism
3. Concrete violation examples
4. Database-only context
5. Automated hallucination tests

**Impossible ❌**
1. 100% accuracy guarantee
2. Remove training data from model
3. Fully deterministic responses
4. Real-time fact-checking

**Your Responsibility 🎯**
1. Treat responses as advisory, not authoritative
2. Verify critical information
3. Run validation tests periodically
4. Use SQL mode for exact lookups
5. Report suspected hallucinations

**Remember:** Hallucination reduction is continuous, not one-time.
