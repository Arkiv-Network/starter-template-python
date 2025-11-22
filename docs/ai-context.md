# AI Assistant Context

👉 **See [../.github/copilot-instructions.md](../.github/copilot-instructions.md) for complete AI context and coding conventions.**

This document redirects to the canonical AI instructions to maintain a single source of truth across all AI assistants (Copilot, Cursor, Claude, ChatGPT, Cody, Aider, etc.).

---

## What's Included

The main instructions file provides comprehensive context for AI-assisted development:

### Critical Information
- **Three naming conventions**: Python SDK (snake_case), Query syntax ($snake_case), Contract events (camelCase)
- **API return values**: Correct tuple unpacking for create_entity()
- **Entity attributes**: entity.key (not .id), entity.payload (not .content)
- **Account management**: Use NamedAccount, not LocalAccount

### Common Patterns
- Creating entities with attributes
- Querying with system ($) and user attributes
- Listening to blockchain events
- Time conversions and TTL management

### Testing & Execution
- Run examples as modules: `uv run python -m arkiv_starter.XX`
- Use pytest fixtures from conftest.py
- Parallel test execution: `uv run pytest -n auto`
- Known limitations of local nodes

### Troubleshooting
- Import errors and interpreter selection
- Transaction failures and debugging
- Entity not found issues
- Type checking with provider casting

---

## For Human Developers

This file is primarily for AI assistants, but human developers can also benefit:
- Quick reference for naming conventions
- Common mistake patterns to avoid
- Example code snippets for typical tasks
- Testing and execution guidelines

---

## Maintenance

This is a **pointer file**. To update AI context:
1. Edit `.github/copilot-instructions.md` (the canonical source)
2. All AI tools will automatically use the updated content
3. No need to update this file or `.cursorrules`

---

*Last updated: 2025-11-22*
*Part of the Arkiv Python Starter template's AI-first development approach*
