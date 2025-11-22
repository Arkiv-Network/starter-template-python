# AI-First Template TODOs

Quick reference for enhancing this starter repo for AI-assisted development.

---

## 🎯 Remaining High-Impact Items

### 1. Prompt Templates

**`PROMPTS.md`** - Copy-paste prompts for common tasks
```markdown
# Arkiv Development Prompts

## Creating Entities
"Store this JSON data on-chain with a 7-day expiration: {json_data}"

## Querying
"Show me all entities owned by {address} with content_type 'application/json'"

## Event Handling
"Listen for new entities created in the last 10 blocks and print their keys"

## Troubleshooting
"My transaction failed with error: {error}. Help me debug."
```

---

## 📚 Documentation Improvements

### 4. Consolidate API_REFERENCE.md

**Current issue:** 90% overlap with README creates maintenance burden

**Options:**
- **A)** Merge into README, keep API_REFERENCE as pure method signatures only
- **B)** Keep API_REFERENCE comprehensive, make README a quickstart only
- **Recommended:** Option A - developers expect README to be comprehensive

### 5. Add "Next Steps" Comments to Examples

In each numbered example, add:
```python
# 🎯 Try This Next:
# 1. Change expires_in to see different TTL values
# 2. Add custom attributes like {"priority": 1, "category": "test"}
# 3. Query with: client.arkiv.query_entities('priority > 0')
```

### 6. API Quick Reference Table

Add to README:
```markdown
## Quick API Reference

| Task | Method | Example |
|------|--------|---------|
| Store data | `create_entity()` | `client.arkiv.create_entity(payload=b"data", expires_in=3600)` |
| Get one item | `get_entity()` | `client.arkiv.get_entity(entity_key)` |
| Search/filter | `query_entities()` | `client.arkiv.query_entities('$owner = "0x..."')` |
| Watch changes | `watch_entity_created()` | `client.arkiv.watch_entity_created(callback)` |
```

---

## 🧪 Testing Enhancements

### 7. Add Tests for Remaining Examples

**Currently tested:** 01_basic_crud, 02_queries, utilities

**Missing:**
- `test_03_events.py` - Event watching patterns
- `test_04_web3_integration.py` - Direct contract interaction

**Note:** Current tests are actually good examples! They show:
- Time conversion utilities
- Entity existence checks
- Extension patterns
- Field mask usage

### 8. Test for Common Mistakes

Add tests that catch typical errors:
```python
def test_content_type_in_query():
    """Ensure snake_case used in queries (common AI mistake)."""
    # Should use $content_type not $contentType
    result = client.arkiv.query_entities('$content_type = "text/plain"')
    assert len(list(result)) >= 0  # Should not raise error

def test_event_arg_naming():
    """Document that event args use camelCase."""
    # This test is documentation for AI
    pass
```

---

## 🚀 Advanced Patterns

### 9. Common Patterns Library (Optional)

**`src/arkiv_patterns/`** - Reusable entity schemas
```python
# patterns/chat_message.py
def create_chat_message(client, channel_id, user_id, text, expires_days=30):
    """Create standardized chat message entity."""
    return client.arkiv.create_entity(
        payload=json.dumps({"text": text}).encode(),
        content_type="application/json",
        attributes={
            "channelId": channel_id,
            "userId": user_id,
            "messageType": "text"
        },
        expires_in=client.arkiv.to_seconds(days=expires_days)
    )
```

### 10. Interactive Playground

**`playground.py`** - Scratch file for AI to suggest experiments
```python
"""
Playground for experimenting with Arkiv.
AI assistants can suggest adding code snippets here.
"""
from arkiv import Arkiv

# Uncomment to start:
# with Arkiv() as client:
#     # Your experiments here
#     pass
```

---

## 🎨 Visual/Media

### 11. Demo GIF or Video

- **README.md**: Embed 60-second demo showing repo → run → output
- AI can't create this but can prompt maintainer to add it
- Huge impact on first impressions

---

## 🔍 Troubleshooting Resources

### 12. Common Issues Flowchart

Add to README or separate `TROUBLESHOOTING.md`:
```markdown
## Debugging Guide

**"Transaction failed"**
→ Check balance: `client.eth.get_balance(account.address)`
→ Check gas: Add `tx_params={"gas": 500000}`
→ Check payload size: Must be < 120KB total transaction size

**"Entity not found"**
→ Verify entity key format (should be int)
→ Check if entity expired
→ Use `entity_exists()` to confirm

**"Import errors"**
→ Run: `uv sync`
→ Select interpreter: Ctrl+Shift+P → "Python: Select Interpreter"
→ Choose `.venv/bin/python`
```

---

## 📊 Priority Matrix

| Priority | Effort | Impact | Item |
|----------|--------|--------|------|
| 🔴 HIGH | Low | High | #2 - Prompt Templates (PROMPTS.md) |
| 🔴 HIGH | Medium | High | #3 - Mini Chat Example |
| 🟡 MEDIUM | Low | Medium | #5 - "Next Steps" Comments |
| 🟡 MEDIUM | Low | Medium | #6 - Quick Reference Table |
| 🟡 MEDIUM | Medium | Medium | #4 - Consolidate API_REFERENCE |
| 🟢 LOW | Medium | Low | #9 - Patterns Library |
| 🟢 LOW | High | Medium | #11 - Demo GIF |

---

## Implementation Order

**Week 1 (Immediate wins):**
2. Create `PROMPTS.md` (1 hour)
3. Add "Next Steps" comments to existing examples (30 min)

**Week 2 (Core value):**
4. Build `examples/mini_chat/` (3-4 hours)
5. Add Quick Reference table to README (1 hour)

**Week 3 (Polish):**
6. Consolidate API_REFERENCE.md (2 hours)
7. Add troubleshooting section (1 hour)

**Ongoing:**
- Collect user questions → add to PROMPTS.md
- Update AI context files as API evolves
- Add tests for newly discovered edge cases

---

## Success Metrics

How to know these improvements work:

- **AI agents make fewer naming mistakes** (snake_case vs camelCase)
- **New users complete first example < 5 min** (already good, maintain)
- **Support questions decrease** (troubleshooting guide helps)
- **GitHub stars/forks increase** (better discoverability)
- **AI can build basic apps without human intervention** (mini_chat as reference)

---

## Notes

- This repo is already **8/10** - these are optimizations, not fixes
- Focus on items that reduce friction for AI-assisted development
- Don't over-engineer - keep examples simple and runnable
- Documentation for AI ≠ documentation for humans (both matter!)

---

## ✅ Already Completed

- Dev container with zero-config setup
- Progressive examples (01→02→03→04)
- Copilot extensions pre-installed
- "For AI Agents" section in README
- Comprehensive API documentation
- Working CI with matrix testing (Python 3.12, 3.14)
- Test examples showing patterns (utilities, field masks, entity lifecycle)
- **✅ AI Context Files** (`.github/copilot-instructions.md`, `.cursorrules`, `docs/ai-context.md`)
  - Naming conventions (Python/Queries/Events)
  - Common misconceptions (Dune/Graph comparison, database assumptions)
  - API return values and patterns
  - What is Arkiv and when to use it
  - Module execution patterns
- **✅ GitHub Actions CI workflow** with Python 3.12 and 3.14 matrix testing
- **✅ Type-safe provider casting** in examples (IDE compatibility)
