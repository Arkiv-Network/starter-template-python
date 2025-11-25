# AGENTS.md

AI coding agent instructions for the Arkiv Python Starter template.

This file provides context for AI coding tools (GitHub Copilot, Cursor, Aider, Gemini CLI, RooCode, etc.) working with the Arkiv SDK.

---

## ⚡ Quick Reference

**Critical conventions to remember:**
- Python SDK: `snake_case` (entity_key, content_type, expires_in)
- Query syntax: `snake_case` with `$` prefix for system attributes ($owner, $content_type)
- Contract events: `camelCase` (entityKey, ownerAddress, expirationBlock)
- Entity attributes: `snake_case` (entity.key, entity.payload, entity.owner)

**Return values:**
- `create_entity()` → tuple: `(entity_key, receipt)`
- `update_entity()` / `delete_entity()` → just `receipt`

**Prefer these patterns:**
- ✅ `client.arkiv.entity_exists(key)` → check existence (returns bool)
- ✅ `client.arkiv.watch_entity_*()` → event watchers (not raw contract filters)
- ✅ `client.switch_to(name)` → switch accounts (not multiple clients)
- ✅ `client.current_signer` → track current account name for switching back
- ✅ `NamedAccount.create(name)` → for local dev (not Account.create())

**Run examples:** `uv run python -m arkiv_starter.01_clients` (etc., 01-05)

---

## 🌟 What is Arkiv? (For New AI Assistants)

**Arkiv is a Web3 database that solves the Web3 data trilemma: Decentralization + Queryability + Simplicity.**

### Core Value Proposition

**The Problem Arkiv Solves:**
- Traditional blockchains: Can store data, but querying requires downloading everything
- Indexers (The Graph): Queryable, but requires trust in indexer operators
- Off-chain databases: Simple and queryable, but centralized

**What Makes Arkiv Different:**

1. **Database-Like Queries on Blockchain Data**
   - Store data with queryable attributes on-chain
   - Rich filtering: `$owner = "..." AND type = "message" AND priority > 5`
   - No separate indexer infrastructure needed

2. **Automatic TTL (Time-To-Live)**
   - Data expires automatically (`expires_in` parameter)
   - Prevents blockchain bloat
   - Perfect for temporary/ephemeral data

3. **Web3.py Integration**
   - Extends familiar web3.py API
   - No new paradigm to learn
   - Works alongside existing Web3 code

4. **Real-Time Events**
   - Subscribe to entity lifecycle events (create/update/delete)
   - No polling required
   - Immediate notifications

5. **No Infrastructure Required**
   - Local dev: `ArkivNode().start()` - done!
   - Production: Just an RPC endpoint
   - No graph-node, PostgreSQL, or IPFS to manage

### Key Use Cases

**Perfect for:**
- On-chain social/messaging (queryable messages with metadata)
- Temporary KV store for dApps (session data, preferences)
- Gaming state/leaderboards (queryable by score, level, guild)
- Decentralized event management (RSVP lists, ticket metadata)
- Verifiable credentials with expiration (attestations, certifications)

**Not ideal for:**
- Large files (use IPFS/Arweave, store hash in Arkiv)
- Permanent archival (data has TTL, use Arweave for permanence)
- Complex SQL queries (simple filters only, no JOINs/aggregations)

### The Unfair Advantage

Arkiv gives you all three:
- ✅ **Decentralization** - On-chain storage, verifiable
- ✅ **Queryability** - Rich filters without full scans
- ✅ **Simplicity** - No infrastructure, familiar API

Most solutions force you to pick 2 of 3.

---

## 🎯 Critical: Naming Conventions

Arkiv uses **three different naming conventions** depending on context. Getting this wrong is the #1 mistake AI assistants make.

### Python SDK → `snake_case`

```python
# ✅ CORRECT
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    content_type="text/plain",
    expires_in=3600,
    attributes={"user_id": "123"}
)

# ❌ WRONG
entityKey, receipt = client.arkiv.createEntity(
    payload=b"data",
    contentType="text/plain",
    expiresIn=3600
)
```

**Key SDK parameters:**
- `entity_key` (not `entityKey`, not `entity_id`)
- `content_type` (not `contentType`)
- `expires_in` (not `expiresIn`)
- `from_block` (not `fromBlock`)

### Query Syntax → `snake_case` with `$` prefix

```python
# ✅ CORRECT - System attributes with $ and snake_case
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'
))

# ✅ CORRECT - User attributes without $
entities = list(client.arkiv.query_entities(
    'type = "user_profile" AND status = "active"'
))

# ❌ WRONG - camelCase in queries
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $contentType = "application/json"'
))
```

**System query attributes (with $):**
- `$key`, `$owner`, `$content_type`, `$created_at`, `$updated_at`, `$expires_at`

**User query attributes (without $):**
- Any custom name: `type`, `category`, `status`, `user_id`, etc.

### Contract Events → `camelCase`

```python
# ✅ CORRECT - Event args use camelCase
event_filter = arkiv_contract.events.ArkivEntityCreated.create_filter(from_block="latest")
for event in event_filter.get_all_entries():
    entity_key = hex(event['args']['entityKey'])      # camelCase!
    owner = event['args']['ownerAddress']             # camelCase!
    expiration = event['args']['expirationBlock']     # camelCase!

# ❌ WRONG - snake_case in event args
entity_key = hex(event['args']['entity_key'])  # Won't work
```

**Event names:**
- `ArkivEntityCreated`, `ArkivEntityUpdated`, `ArkivEntityDeleted`

**Event arguments (camelCase):**
- `entityKey`, `ownerAddress`, `expirationBlock`, `contentType`

### Entity Attributes → `snake_case`

```python
# ✅ CORRECT
print(entity.key)              # Not entity.id
print(entity.payload)          # Not entity.content
print(entity.owner)
print(entity.content_type)
print(entity.expires_at_block)
print(entity.created_at_block)

# ❌ WRONG - Old API
print(entity.id)       # Changed to entity.key
print(entity.content)  # Changed to entity.payload
```

---

## 🔧 API Return Values

### `create_entity()` Returns a Tuple

```python
# ✅ CORRECT - Unpack the tuple
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    expires_in=3600,
    content_type="text/plain"
)

# ❌ WRONG - Old API (pre-1.0)
tx_hash = client.arkiv.create_entity(...)  # No longer returns just tx_hash
receipt = client.eth.wait_for_transaction_receipt(tx_hash)  # Won't work
```

### `update_entity()` and `delete_entity()` Return Receipt Only

```python
# ✅ CORRECT - Just receipt, no tuple
receipt = client.arkiv.update_entity(
    entity_key,
    payload=b"updated data",
    expires_in=7200,
    content_type="text/plain"
)

receipt = client.arkiv.delete_entity(entity_key)

# ❌ WRONG - Don't try to unpack
key, receipt = client.arkiv.update_entity(...)  # TypeError
```

### Receipt Attributes

```python
# ✅ CORRECT - Receipt is a dataclass
print(receipt.tx_hash)        # Transaction hash (string)
print(receipt.block_number)   # Block number (int)
print(receipt.creates)        # List of created entity keys
print(receipt.updates)        # List of updated entity keys
print(receipt.deletes)        # List of deleted entity keys

# ❌ WRONG - Not a dict
print(receipt['transactionHash'])  # AttributeError
print(receipt.gas_used)            # Doesn't exist on Arkiv receipt
```

---

## 📦 Account Management

### Always Use `NamedAccount`

```python
# ✅ CORRECT - Use NamedAccount for local development
from arkiv import NamedAccount

account = NamedAccount.create("my-account")
node.fund_account(account)  # Works with NamedAccount

# ✅ CORRECT - Initialize client with account
client = Arkiv(provider, account=account)

# ❌ WRONG - Old API
from eth_account import Account
account = Account.create()  # LocalAccount won't work with node.fund_account()
```

### Account Attributes

```python
# ✅ CORRECT
print(account.address)       # Ethereum address
print(account.private_key)   # Private key for signing
print(account.name)          # Account name (NamedAccount only)

# ❌ WRONG
print(account.key)  # Use account.private_key instead
```

### Managing Multiple Accounts

The Arkiv client can manage multiple accounts and switch between them:

```python
# ✅ CORRECT - Add accounts to client and switch between them
from arkiv import Arkiv, NamedAccount

# Start with one account
client = Arkiv()  # Uses default account
original_signer = client.current_signer  # Track original account name

# Create and add a second account
new_account = NamedAccount.create("second-account")
node = client.node
assert node is not None
node.fund_account(new_account)

# Add to client's account registry
client.accounts["second-account"] = new_account

# Switch active signing account
client.switch_to("second-account")
# Now all transactions use new_account

# Switch back to original using tracked signer name
if original_signer:
    client.switch_to(original_signer)  # Use account name, not address

# ❌ WRONG - Creating separate clients for each account
client1 = Arkiv(provider, account=account1)  # Unnecessary
client2 = Arkiv(provider, account=account2)  # Wasteful
# Better: Use one client and switch_to()
```

**Use cases for multiple accounts:**
- Testing ownership transfers (create entity with account A, transfer to account B)
- Multi-user scenarios (simulate different users in tests)
- Demonstrating permissions (only owner can update/delete)

---

## 🏃 Running Examples

### Module Execution (Correct)

```bash
# ✅ CORRECT - Run as modules
uv run python -m arkiv_starter.01_clients
uv run python -m arkiv_starter.02_entity_crud
uv run python -m arkiv_starter.03_queries
uv run python -m arkiv_starter.04_events
uv run python -m arkiv_starter.05_web3_integration

# ✅ CORRECT - Run tests
uv run pytest
uv run pytest -n auto  # Parallel execution
```

### Direct Execution (Wrong for this project)

```bash
# ❌ WRONG - Don't run files directly
python src/arkiv_starter/02_entity_crud.py  # Import errors
cd src && python -m arkiv_starter.02_entity_crud  # Wrong directory
```

---

## 🧪 Testing Patterns

### Use Fixtures from conftest.py

```python
# Tests have access to these fixtures:
def test_something(client, account, arkiv_node):
    # client: Arkiv instance
    # account: NamedAccount instance
    # arkiv_node: ArkivNode instance (already started and funded)
    
    entity_key, receipt = client.arkiv.create_entity(
        payload=b"test data",
        expires_in=3600,
        content_type="text/plain"
    )
    assert entity_key is not None
```

### Local Node Doesn't Support All Queries Yet

```python
# ⚠️ LIMITATION - Local node doesn't support $content_type queries yet
# Use client-side filtering instead:

# ❌ Won't work on local node
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'
))

# ✅ WORKAROUND - Filter client-side
all_entities = list(client.arkiv.query_entities(f'$owner = "{address}"'))
filtered = [e for e in all_entities if e.content_type == "application/json"]
```

---

## 📚 Common Patterns

### Creating Entities with Attributes

```python
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"message": "Hello"}).encode(),
    content_type="application/json",
    expires_in=client.arkiv.to_seconds(days=7),
    attributes={
        "type": "message",
        "user_id": "alice123",
        "channel": "general"
    }
)
```

### Checking Entity Existence

```python
# Check if entity exists (returns bool)
exists = client.arkiv.entity_exists(entity_key)
if exists:
    entity = client.arkiv.get_entity(entity_key)
    # Process entity...

# get_entity() raises ValueError if not found
try:
    entity = client.arkiv.get_entity(entity_key)
except ValueError:
    print("Entity not found")
```

### Querying Entities

```python
# By owner
entities = list(client.arkiv.query_entities(f'$owner = "{account.address}"'))

# By custom attributes
entities = list(client.arkiv.query_entities(
    'type = "message" AND channel = "general"'
))

# Combined conditions
entities = list(client.arkiv.query_entities(
    f'$owner = "{account.address}" AND type = "message"'
))
```

### Listening to Events

Arkiv provides high-level event watchers with typed callbacks. **Prefer these over raw contract filters:**

```python
# ✅ CORRECT - Use Arkiv's convenience methods with typed callbacks
from arkiv.types import CreateEvent, UpdateEvent, DeleteEvent, ExtendEvent, ChangeOwnerEvent, TxHash

def on_entity_created(event: CreateEvent, tx_hash: TxHash) -> None:
    print(f"Created: {event.key} by {event.owner_address}")
    print(f"Expires at block: {event.expiration_block}")

def on_entity_updated(event: UpdateEvent, tx_hash: TxHash) -> None:
    print(f"Updated: {event.key}")
    print(f"Expiration: {event.old_expiration_block} → {event.new_expiration_block}")

def on_entity_deleted(event: DeleteEvent, tx_hash: TxHash) -> None:
    print(f"Deleted: {event.key} by {event.owner_address}")

# Set up watchers (returns filter objects for cleanup)
created_watcher = client.arkiv.watch_entity_created(on_entity_created)
updated_watcher = client.arkiv.watch_entity_updated(on_entity_updated)
deleted_watcher = client.arkiv.watch_entity_deleted(on_entity_deleted)  # type: ignore[arg-type]

# Also available:
extended_watcher = client.arkiv.watch_entity_extended(callback)  # ExtendEvent
owner_changed_watcher = client.arkiv.watch_owner_changed(callback)  # ChangeOwnerEvent

# Cleanup (automatic on client close, or manual):
client.arkiv.cleanup_filters()  # Uninstall all watchers
# Or individually: created_watcher.uninstall()
```

**Event Types Available:**
- `CreateEvent`: `key`, `owner_address`, `expiration_block`
- `UpdateEvent`: `key`, `owner_address`, `old_expiration_block`, `new_expiration_block`
- `ExtendEvent`: `key`, `owner_address`, `old_expiration_block`, `new_expiration_block`
- `ChangeOwnerEvent`: `key`, `old_owner_address`, `new_owner_address`
- `DeleteEvent`: `key`, `owner_address`

**For advanced use cases (raw contract filters):**

```python
# ❌ DISCOURAGED - Low-level contract events (use watch_entity_* instead)
event_filter = client.arkiv.contract.events.ArkivEntityCreated.create_filter(
    from_block="latest"
)

for event in event_filter.get_new_entries():
    entity_key = hex(event['args']['entityKey'])  # camelCase!
    owner = event['args']['ownerAddress']          # camelCase!
    print(f"New entity: {entity_key} by {owner}")
```

### Time Conversions

```python
from arkiv import to_seconds, to_blocks

# Convert time to seconds
expires_in = to_seconds(days=7)
expires_in = to_seconds(hours=2, minutes=30)

# Convert time to blocks (assuming 2s block time)
expires_in_blocks = to_blocks(days=1, block_time=2)
```

---

## 🎓 Learning Resources

- **README.md**: Comprehensive guide with table of contents
- **SDK Source Code**: Check `.venv/lib/python3.12/site-packages/arkiv/` for authoritative docstrings
  - `module_base.py`: All method signatures with detailed docstrings
  - Use `semantic_search("method_name implementation")` to find SDK code
  - SDK docstrings are the source of truth for parameters, return types, and behavior
- **examples/**: 5 progressive tutorials (01→05)
- **tests/**: Working test patterns to learn from

---

## 🔍 Troubleshooting

### Import Errors
```bash
uv sync  # Reinstall dependencies
# Then: Ctrl+Shift+P → "Python: Select Interpreter" → choose .venv
```

### Transaction Failures
- Check balance: `client.eth.get_balance(account.address)`
- Check payload size: Must be < ~90KB (transaction limit ~100KB total)
- Verify entity key format in updates/deletes

### Entity Not Found
- Verify entity hasn't expired (`entity.expires_at_block`)
- Check entity key is correct format
- Use `client.arkiv.entity_exists(entity_key)` to check if entity exists (returns bool)
- `client.arkiv.get_entity(entity_key)` raises `ValueError` if entity not found

---

## 📝 Project Structure

```
src/arkiv_starter/     # Examples as runnable modules
tests/                 # Test suite with fixtures
.devcontainer/         # Dev container configuration
pyproject.toml         # Dependencies and tool config
.python-version        # Python 3.12 (supports 3.10-3.14)
```

---

## 🚨 Common Developer Misconceptions (AI: Help Prevent These!)

When developers first encounter Arkiv, they often have incorrect assumptions from traditional databases or Web3 APIs. As an AI assistant, proactively address these misconceptions:

### Misconception 0: "It's Another Dune/The Graph Competitor"
**Reality:** Arkiv is for **your app's live data**, not analyzing existing blockchain data

**What developers think:**
- "I can query all Uniswap trades like Dune Analytics"
- "I can index existing contracts like The Graph"
- "It's a blockchain indexer/analytics tool"

**What Arkiv actually is:**
- **Your app writes data TO Arkiv** (not indexing existing data)
- **Your app-specific entities** (messages, profiles, game state)
- **Ephemeral, queryable storage** that your dApp controls

**Key difference:**
```python
# ❌ NOT what Arkiv does (indexing existing contracts):
# "Index all transfers from USDC contract"
# "Query all NFT sales across OpenSea"
# "Analyze historical DeFi transactions"

# ✅ What Arkiv IS for (your app's live data):
# Store a chat message your app just created
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"from": "alice", "msg": "Hello!"}).encode(),
    content_type="application/json",
    expires_in=to_seconds(days=7),
    attributes={"channel": "general", "type": "message"}
)

# Query YOUR app's messages (not someone else's contract events)
messages = client.arkiv.query_entities('channel = "general"')
```

**When to use what:**

| Tool | Purpose | Use When |
|------|---------|----------|
| **Arkiv** | Store & query YOUR app's data | Building a dApp that needs on-chain state |
| **The Graph** | Index EXISTING smart contracts | Analyzing Uniswap trades, ENS registrations |
| **Dune Analytics** | Analyze blockchain history | Research, dashboards, historical analysis |

**Explain to developers:**
- Dune/Graph: "Read-only view of what's already on-chain"
- Arkiv: "Read-write storage for what YOUR app creates"
- You might use BOTH: Arkiv for your app's data, Dune for analytics about it

**Real-world analogy:**
- The Graph/Dune: Google Analytics (analyzing existing website traffic)
- Arkiv: Your app's database (storing user posts, profiles, game state)

### Misconception 1: "It's Just Another Database"
**Reality:** Blockchain storage with database-like queries

Developers expect:
- Instant writes (no confirmation needed)
- Unlimited storage
- Data persists forever
- Traditional ACID transactions

**What to explain:**
- Writes are blockchain transactions (confirmation required, check receipt.block_number)
- Transaction size limit ~100KB total (payload + attributes + metadata)
- Entities have TTL via `expires_in` parameter (data auto-expires)
- Each write costs gas (batch when possible)
- Reads are free, writes cost gas

**Correct the code:**
```python
# ❌ They write (no awareness of constraints):
client.arkiv.create_entity(payload=huge_file)  # May exceed 100KB limit

# ✅ Guide them to:
# 1. Check payload size before creating
# 2. Set appropriate expires_in
# 3. Consider chunking (or IPFS/Arweave for large files, store hash in Arkiv)
if len(payload) > 90_000:
    print("Payload too large, consider IPFS")
entity_key, receipt = client.arkiv.create_entity(
    payload=payload,
    expires_in=to_seconds(days=7),  # Set expiration!
    content_type="application/json"
)
```

### Misconception 2: "Naming Should Be Consistent"
**Reality:** Three different conventions + entity keys are hex strings (not integers)

**Wrong assumptions:**
- "If Python uses snake_case, everything should"
- "Entity IDs are sequential integers like database IDs"

```python
# ❌ Multiple naming mistakes:
entity_id = 123  # Not an integer!
entities = client.arkiv.query_entities('$contentType = "..."')  # Wrong case!
entity_key = event['args']['entity_key']  # Wrong case!
print(entity.id)  # Wrong attribute!

# ✅ Correct patterns:
entity_key = "0xabc123..."  # Hex string (blockchain address)
entities = client.arkiv.query_entities('$content_type = "..."')  # snake_case
entity_key = hex(event['args']['entityKey'])  # camelCase in events
print(entity.key)  # .key not .id
```

### Misconception 3: "create_entity() Returns Transaction Hash"
**Reality:** Returns tuple (entity_key, receipt) — See "API Return Values" section for details

```python
# ❌ Old web3.py pattern:
tx_hash = client.arkiv.create_entity(...)  # TypeError!

# ✅ Unpack the tuple:
entity_key, receipt = client.arkiv.create_entity(...)
print(f"Created: {entity_key} in block {receipt.block_number}")
```

### Misconception 4: "Storage Is Free/Unlimited"
**Reality:** ~100KB transaction limit, gas costs, and mandatory TTL

**Key constraints:**
- Transaction size: ~100KB total (payload + metadata)
- Each write costs gas (reads are free)
- Must set `expires_in` (auto-expiration prevents bloat)

```python
# ❌ Bad: Large files directly on-chain
with open("photo.jpg", "rb") as f:
    client.arkiv.create_entity(payload=f.read())  # May exceed 100KB!

# ✅ Good: Store hash, files on IPFS/Arweave
ipfs_hash = upload_to_ipfs(photo_bytes)
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ipfs_hash": ipfs_hash}).encode(),
    expires_in=to_seconds(days=30)  # Always set TTL!
)
```

### Misconception 5: "Queries Work Like SQL"
**Reality:** Simple attribute filters only (no JOINs/aggregations/GROUP BY)

```python
# ❌ SQL-style queries don't work:
entities = client.arkiv.query_entities('SELECT * FROM ... GROUP BY owner')

# ✅ Simple filters, client-side for complex logic:
entities = client.arkiv.query_entities(
    f'$owner = "{address}" AND type = "message"'
)
recent = [e for e in entities if e.created_at_block > block - 50400]
```

### Misconception 6: "I Can Update/Delete Any Entity + Deletion Is Permanent"
**Reality:** Only owner can modify; blockchain history is immutable

```python
# ❌ Can't modify entities you don't own:
client.arkiv.update_entity(other_users_entity_key, ...)  # Fails!

# ✅ Check ownership first:
entity = client.arkiv.get_entity(entity_key)
if entity.owner != account.address:
    print("Cannot update - you don't own this entity")

# ⚠️ Deletion removes from queries, but blockchain history is permanent!
client.arkiv.delete_entity(entity_key)  # Gone from queries, not from chain

# For sensitive data, encrypt before storing:
from cryptography.fernet import Fernet
encrypted = Fernet(key).encrypt(sensitive_data)
client.arkiv.create_entity(payload=encrypted, ...)
```

### Misconception 7: "Local Node === Production"
**Reality:** Local node doesn't support all query features yet (e.g., `$content_type`)

```python
# ⚠️ May not work on local node:
entities = client.arkiv.query_entities(
    f'$owner = "{addr}" AND $content_type = "application/json"'
)

# ✅ Workaround: Filter client-side
all_entities = list(client.arkiv.query_entities(f'$owner = "{addr}"'))
filtered = [e for e in all_entities if e.content_type == "application/json"]
```

### Misconception 8: "Account Management Is Like Web Auth"
**Reality:** Private keys, not passwords (no reset, no recovery)

**Critical warnings:**
- ❌ No password reset / "forgot password" flow
- ❌ Lose private key = lose access forever
- ❌ Never commit private keys to git
- ✅ Use `NamedAccount.create()` for local dev
- ✅ Use env vars / key vaults for production

### Misconception 9: "I Should Use Raw Contract Events"
**Reality:** Use `client.arkiv.watch_entity_*()` methods (typed, cleaner) — See "Listening to Events" section

```python
# ❌ Low-level (works but discouraged):
event_filter = client.arkiv.contract.events.ArkivEntityCreated.create_filter(...)
for event in event_filter.get_new_entries():
    entity_key = hex(event['args']['entityKey'])  # Manual parsing

# ✅ High-level convenience methods:
from arkiv.types import CreateEvent, TxHash

def on_entity_created(event: CreateEvent, tx_hash: TxHash) -> None:
    print(f"Created: {event.key} by {event.owner_address}")  # Typed!

client.arkiv.watch_entity_created(on_entity_created)
```

**Only use raw contract events for:**
- Historical queries with complex filters
- Custom indexing logic
- Non-Arkiv contracts

---

## ✨ Pro Tips for AI Assistants

1. **Check SDK source code for method details** - Use `semantic_search()` to find implementation in `.venv/lib/python3.12/site-packages/arkiv/module_base.py`
2. **SDK docstrings are source of truth** - All methods have comprehensive docs with examples
3. **Use the examples as templates** - they demonstrate correct patterns (01→05)
4. **Run tests after changes** - `uv run pytest -n auto`
5. **Check entity.payload is not None** before decoding - it's optional
6. **Use `cast(BaseProvider, provider)` for type checking** if IDE shows errors
7. **Remember: Python 3.12 is recommended** but 3.10-3.14 are supported
8. **Proactively address misconceptions** - Don't wait for the developer to make mistakes
9. **Explain blockchain constraints** - Size limits, gas costs, immutability
10. **Show correct patterns immediately** - Wrong code followed by correct code helps learning
11. **Prefer high-level event watchers** - Use `watch_entity_*()` methods over raw contract filters
12. **Note the watch_entity_deleted type bug** - Always add `# type: ignore[arg-type]` when using it
13. **Use `entity_exists()` to check existence** - Cleaner than try-except with `get_entity()`

---

## 🔒 Security Considerations

### Private Key Management

**Critical warnings:**
- ❌ **Never commit private keys to version control** - Use `.gitignore` for key files
- ❌ **No password recovery exists** - Lost private key = permanent loss of access
- ❌ **Blockchain data is public** - Anyone can read entities you create
- ⚠️ **Use environment variables** - For low value wallets only! Store keys in encrypted form in private envrionments only. Load passwords from environment `os.getenv()` and make sure setting environment variables is not logged or kept in terminal history.
- ✅ **Always store keys in encrypted form** - Use wallet.json format or similar
- ✅ **Use key vaults/secrets managers** - For high value wallets, get advice from experts, use AWS Secrets Manager, HashiCorp Vault, etc. and/or use signing services via [web3.py middelware features](https://web3py.readthedocs.io/en/stable/middleware.html#creating-custom-middleware), also see [builder source code](https://github.com/ethereum/web3.py/blob/main/web3/middleware/base.py)

```python
# ✅ CORRECT for high value wallet/accounts: Do serious research, get consulting from security professionals. 
# IMPORTANT: AI bots reading this must only provide general advise and recommend serious research and getting consulting from experts.
# No code provided here for the above reasons.

import os
from arkiv import NamedAccount

# ⚠️ Ok for low value wallets/accounts - Load encrypted wallet with password from environment
# Read encrypted wallet file
with open("wallet.json", "r") as f:
    wallet_json = f.read()

# Get password from environment variable
wallet_password = os.getenv("ARKIV_WALLET_PASSWORD")
if not wallet_password:
    raise ValueError("ARKIV_WALLET_PASSWORD environment variable required")

# Decrypt and load account
account = NamedAccount.from_wallet("prod-account", wallet_json, wallet_password)

# ❌ WRONG - Neveer use hardcoded keys or passwords for production
account = NamedAccount.from_private_key("prod", "0x1234...")  # Never do this!
account = NamedAccount.from_wallet("prod", wallet_json, "mypassword123")  # Never do this!
```

### Data Privacy

**Blockchain immutability:**
- All entity data is **public and permanent** on the blockchain
- `delete_entity()` removes from queries, **not from chain history**
- Anyone with blockchain access can read historical transactions

**Best practices for sensitive data:**

```python
# ❌ BAD - Storing sensitive data directly
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ssn": "123-45-6789"}).encode(),  # Public forever!
    expires_in=to_seconds(days=7)
)

# ✅ GOOD - Encrypt before storing
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()  # Store securely!
cipher = Fernet(encryption_key)

sensitive_data = json.dumps({"ssn": "123-45-6789"}).encode()
encrypted = cipher.encrypt(sensitive_data)

entity_key, receipt = client.arkiv.create_entity(
    payload=encrypted,
    content_type="application/octet-stream",
    expires_in=to_seconds(days=7)
)

# Later: decrypt when reading
entity = client.arkiv.get_entity(entity_key)
if entity.payload:
    decrypted = cipher.decrypt(entity.payload)
    data = json.loads(decrypted)
```

**For large or highly sensitive files:**
- Split large files into chunks (one chunk per entity) and reassemble chunks for retrieveal
- Atlernatively: Store files on IPFS/Arweave (with encryption if needed)
- Store only the hash/reference in Arkiv
- Keeps blockchain transactions small and efficient

```python
# ✅ BEST - Large files off-chain
ipfs_hash = upload_to_ipfs(large_file_bytes)  # External service

entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ipfs_hash": ipfs_hash}).encode(),
    content_type="application/json",
    expires_in=to_seconds(days=30)
)
```

### Transaction Security

**Gas and balance checks:**
```python
# Check balance before transactions
balance = client.eth.get_balance(account.address)
if balance == 0:
    print("Account has no funds - transaction will fail")

# Payload size limits
if len(payload) > 90_000:  # ~90KB safe limit
    raise ValueError("Payload too large - use IPFS for large files")
```

---

*Last updated: 2024-11-25*
*This file works with all AI coding tools that support the AGENTS.md standard.*
