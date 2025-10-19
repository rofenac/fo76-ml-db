# RAG System Enhancements - Phase 1

## Overview

This document describes the enhancements made to the Fallout 76 RAG system to improve user experience and answer quality based on real-world testing feedback.

## Implementation Date

2025-10-19

## Enhancements Implemented

### 1. Query Intent Classification

**What it does:** Automatically detects when user questions are too vague or ambiguous to answer directly.

**Classification Categories:**
- **SPECIFIC** - Clear questions that can be answered immediately
  - Example: "What perks affect the Gauss shotgun?"
- **VAGUE_CRITERIA** - Questions using subjective terms without criteria
  - Example: "What is the best weapon?"
- **VAGUE_BUILD** - Build questions missing playstyle details
  - Example: "What's a good rifle build?"
- **AMBIGUOUS** - Unclear what the user is asking for

**Benefits:**
- No more guessing at user intent
- Reduces incorrect or unhelpful answers
- Guides users to ask better questions

**Implementation:** `FalloutRAG.classify_intent()` in `rag/query_engine.py`

---

### 2. Clarifying Question System

**What it does:** When a vague question is detected, the system asks 2-3 clarifying questions before querying the database.

**Example Flow:**
```
User: "What is the best weapon?"