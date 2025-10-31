# Anti-Hallucination Controls

## Overview

This document explains the technical controls implemented to minimize LLM hallucination and their inherent limitations.

## ⚠️ Critical Limitation

**There is NO way to 100% prevent LLM hallucination.** This is a fundamental characteristic of large language models. They are probabilistic systems that generate text based on patterns, not deterministic databases that retrieve facts.

**What we CAN do:** Implement multiple layers of controls to **significantly reduce** (but never eliminate) hallucination.

---

## Implemented Controls

### 1. Strict System Prompts

**Location:**
- `rag/query_engine.py` (SQL mode, lines 257-286)
- `rag/hybrid_query_engine.py` (Vector mode, lines 561-585)

**Implementation:**
```python
system="""You are a database results formatter. You have ZERO knowledge...

⚠️ CRITICAL: You are STRICTLY FORBIDDEN from using your training data...

ABSOLUTE RULES - NO EXCEPTIONS:
1. You MUST ONLY use data from the database results
2. NEVER mention items not in the database results
3. NEVER speculate about what "might exist"
...
"""
```

**What this does:**
- Explicitly forbids using training data
- Provides concrete examples of violations
- Sets strict boundaries on what the LLM can mention

**Limitations:**
- LLMs don't have perfect instruction following
- May still occasionally "leak" training knowledge
- Cannot enforce 100% compliance

### 2. Low Temperature Setting

**Location:** Both `query_engine.py` and `hybrid_query_engine.py`

**Implementation:**
```python
temperature=0.3  # Low temperature = more deterministic
```

**What this does:**
- Makes responses more deterministic and conservative
- Reduces "creative" outputs that might hallucinate
- Favors high-probability tokens over diverse outputs

**Standard temperature values:**
- `0.0` = Maximum determinism (repetitive, but safest)
- `0.3` = Our setting (good balance)
- `1.0` = Default (more creative, higher hallucination risk)
- `2.0` = Maximum creativity (very high hallucination risk)

**Limitations:**
- Lower temperature reduces creativity but doesn't eliminate hallucination
- Can make responses feel "robotic"
- May miss useful connections in data

### 3. Database-Only Context

**What this does:**
- LLM only receives database results in its context
- No access to external information
- Limited to game mechanics context we explicitly provide

**Limitations:**
- LLM still has training data "baked in"
- Cannot truly "forget" what it learned during training
- May unconsciously blend training knowledge with database results

### 4. Explicit Violation Examples

**Location:** System prompts in both files

**Implementation:**
```
VIOLATION EXAMPLES (DO NOT DO THIS):
❌ "Other perks like Expert Shotgunner might help" - NO!
❌ "You should also consider..." - FORBIDDEN
❌ "Players typically use..." - NO!
```

**What this does:**
- Shows the LLM concrete examples of forbidden behavior
- Helps the LLM recognize and avoid similar patterns
- Provides negative reinforcement

**Limitations:**
- Can only cover a finite set of examples
- LLM may still generate similar but not identical violations

### 5. Conversation History Management

**Location:** Both RAG classes maintain `conversation_history`

**What this does:**
- Keeps last 3 exchanges in context
- Prevents contradictions across conversation
- Maintains consistency

**Limitations:**
- Long conversations may still drift
- History can compound errors if early answers hallucinated

---

## What We CANNOT Do

### ❌ Impossible Controls

1. **100% Hallucination Prevention**
   - LLMs are fundamentally probabilistic
   - Training data is "baked into" the model weights
   - Cannot be truly "unlearned"

2. **Real-time Fact Checking**
   - Would require validating every statement against database
   - Complex statements may blend facts in subtle ways
   - Computational cost would be prohibitive

3. **Model Surgery**
   - Cannot remove Fallout 76 knowledge from model weights
   - Cannot "lobotomize" specific knowledge domains
   - Would require model retraining from scratch

4. **Deterministic Outputs**
   - Even at temperature=0.0, some randomness exists
   - Token selection still probabilistic
   - Different API calls may give different results

---

## Best Practices for Users

### ✅ Do This:

1. **Verify Critical Information**
   - Double-check important stats against the database
   - Use exact queries when precision matters
   - Run validation tests (see `rag/test_no_hallucination.py`)

2. **Use Exact Queries for Facts**
   - "What's the damage of Gauss Shotgun?" → SQL mode (more reliable)
   - "Best bloodied build" → Vector mode (more conceptual)

3. **Watch for Red Flags**
   - "Typically..." or "Usually..." = possible training data leak
   - Items mentioned that weren't in your query results
   - Stats that seem inconsistent with database

4. **Test Edge Cases**
   - Ask about non-existent items
   - Request comparisons with items not in database
   - See if the LLM invents data

### ❌ Don't Do This:

1. **Assume 100% Accuracy**
   - Always maintain healthy skepticism
   - Verify important decisions

2. **Rely Solely on LLM for Critical Paths**
   - Use direct SQL queries for mission-critical data
   - Treat LLM as "advisory" not "authoritative"

3. **Ignore Validation Tests**
   - Run `test_no_hallucination.py` periodically
   - Check for drift over time

---

## Testing for Hallucination

### Automated Tests

**Location:** `rag/test_no_hallucination.py`

**What it tests:**
- Asking about non-existent items
- Requesting comparisons with fake perks
- Verifying the LLM says "not in database" instead of inventing data

**Run tests:**
```bash
cd rag
python test_no_hallucination.py
```

### Manual Testing

**Good test queries:**
```
1. "What's the damage of the Plasma Disruptor?"
   (fake weapon - should say not in database)

2. "Compare Bloodied Fixer to Nuclear Dragon"
   (Nuclear Dragon is fake - should only discuss Fixer)

3. "Best perks for the Vaporizer weapon"
   (fake weapon - should say no data available)
```

**Expected behavior:**
- Should NOT invent stats for fake items
- Should NOT suggest items not in database
- Should clearly state "not available in database"

---

## Technical Tradeoffs

### Strictness vs Usefulness

**More Strict (Current Settings):**
- ✅ Less hallucination
- ✅ More trustworthy for facts
- ❌ May miss useful inferences
- ❌ Can feel overly cautious

**Less Strict (Higher Temperature):**
- ✅ More creative connections
- ✅ Better natural language
- ❌ More hallucination risk
- ❌ Less trustworthy

**Our Choice:** Prioritize trustworthiness over creativity.

### Why We Can't Go Lower

**Temperature < 0.3:**
- Responses become very repetitive
- May refuse to answer valid questions
- User experience suffers significantly

**Why We Can't Add More Validation:**
- Would need to parse every LLM statement
- Match against database (complex for natural language)
- Significant computational overhead
- May introduce false positives (reject valid answers)

---

## Future Improvements (Potential)

### 1. Structured Output Validation
Use Claude's JSON mode to force structured responses:
```json
{
  "items": [
    {"name": "Gauss Shotgun", "damage": 65, "source": "database"}
  ],
  "disclaimer": "All data from database query #1234"
}
```

**Pros:** Easier to validate, harder to hallucinate
**Cons:** Less natural, more rigid

### 2. Two-Pass Verification
1. First pass: Generate answer
2. Second pass: Validate answer against database
3. Return only if validated

**Pros:** Catches many hallucinations
**Cons:** 2x API cost, 2x latency

### 3. Fact Extraction + Validation
1. Extract factual claims from LLM response
2. Generate SQL to verify each claim
3. Reject response if claims don't match

**Pros:** High precision
**Cons:** Very complex, high cost, may reject good answers

### 4. Fine-tuned Model
Train a custom model with examples of:
- Good: Database-only responses
- Bad: Hallucinated responses

**Pros:** Better instruction following
**Cons:** Expensive, requires ongoing maintenance

---

## Summary

### What We've Done ✅

1. ✅ Very strict system prompts with explicit rules
2. ✅ Low temperature (0.3) for determinism
3. ✅ Concrete violation examples
4. ✅ Database-only context (no external data)
5. ✅ Automated hallucination tests

### What We Cannot Do ❌

1. ❌ Guarantee 100% accuracy (fundamentally impossible)
2. ❌ Remove training data from model
3. ❌ Make responses fully deterministic
4. ❌ Real-time fact-check every statement

### What You Should Do 🎯

1. 🎯 Treat LLM responses as advisory, not authoritative
2. 🎯 Verify critical information against database
3. 🎯 Run validation tests periodically
4. 🎯 Report suspected hallucinations for investigation
5. 🎯 Use exact queries (SQL mode) for factual lookups

---

## Questions?

- See `rag/test_no_hallucination.py` for testing
- See `rag/query_engine.py` lines 257-286 for SQL mode prompts
- See `rag/hybrid_query_engine.py` lines 561-585 for Vector mode prompts
- Check conversation history in both classes for context management

**Remember:** Hallucination reduction is a continuous process, not a one-time fix.
