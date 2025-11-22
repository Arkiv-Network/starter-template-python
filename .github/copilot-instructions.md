# AI Assistant Instructions for Arkiv Python Starter

This file provides persistent context for AI coding assistants (GitHub Copilot, Cursor, Claude, etc.) working with the Arkiv SDK.

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

---

## 🏃 Running Examples

### Module Execution (Correct)

```bash
# ✅ CORRECT - Run as modules
uv run python -m arkiv_starter.01_basic_crud
uv run python -m arkiv_starter.02_queries
uv run python -m arkiv_starter.03_events
uv run python -m arkiv_starter.04_web3_integration

# ✅ CORRECT - Run tests
uv run pytest
uv run pytest -n auto  # Parallel execution
```

### Direct Execution (Wrong for this project)

```bash
# ❌ WRONG - Don't run files directly
python src/arkiv_starter/01_basic_crud.py  # Import errors
cd src && python -m arkiv_starter.01_basic_crud  # Wrong directory
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

```python
from arkiv.node import ArkivNode

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

## 🚨 Common Mistakes to Avoid

### ❌ Mistake 1: Wrong Naming Convention
```python
# WRONG - Mixing camelCase in Python
client.arkiv.createEntity(payload=b"data", contentType="text/plain")
```

### ❌ Mistake 2: Wrong Entity Attributes
```python
# WRONG - Old API names
entity.id        # Use entity.key
entity.content   # Use entity.payload
```

### ❌ Mistake 3: Wrong Return Value Handling
```python
# WRONG - Not unpacking tuple
tx_hash = client.arkiv.create_entity(...)
```

### ❌ Mistake 4: Wrong Event Arg Names
```python
# WRONG - snake_case in events
entity_key = event['args']['entity_key']  # Use 'entityKey'
```

### ❌ Mistake 5: Wrong Query Syntax
```python
# WRONG - camelCase in queries
query = '$owner = "..." AND $contentType = "..."'  # Use $content_type
```

---

## 🎓 Learning Resources

- **README.md**: Comprehensive guide with table of contents
- **API_REFERENCE.md**: Complete API documentation
- **examples/**: 4 progressive tutorials (01→04)
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
- Use `client.arkiv.get_entity(entity_key)` - returns None if not found

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
# 3. Consider IPFS/Arweave for large files, store hash in Arkiv
if len(payload) > 90_000:
    print("Payload too large, consider IPFS")
entity_key, receipt = client.arkiv.create_entity(
    payload=payload,
    expires_in=to_seconds(days=7),  # Set expiration!
    content_type="application/json"
)
```

### Misconception 2: "Naming Should Be Consistent"
**Reality:** Three different conventions (Python/Queries/Events)

**What developers assume:**
- "If Python uses snake_case, everything should"
- "Event args should match SDK naming"

**Proactively correct:**
```python
# ❌ Logical but wrong:
entities = client.arkiv.query_entities('$contentType = "..."')
entity_key = event['args']['entity_key']

# ✅ Explain the three conventions:
# - Python SDK: snake_case (content_type, entity_key)
# - Queries: snake_case with $ ($content_type, $owner)
# - Events: camelCase (entityKey, ownerAddress)
entities = client.arkiv.query_entities('$content_type = "..."')
entity_key = hex(event['args']['entityKey'])
```

### Misconception 3: "Entity IDs Are Simple Integers"
**Reality:** Entity keys are hex strings (blockchain addresses)

**They expect:**
```python
entity_id = 123  # Sequential integer
entity = client.arkiv.get_entity(123)
print(entity.id)  # Doesn't exist!
```

**Correct to:**
```python
entity_key = "0xabc123..."  # Hex string
entity = client.arkiv.get_entity(entity_key)
print(entity.key)  # Not .id, use .key
```

### Misconception 4: "create_entity() Returns Transaction Hash"
**Reality:** Returns tuple (entity_key, receipt)

**They write (old web3.py pattern):**
```python
tx_hash = client.arkiv.create_entity(...)  # TypeError!
receipt = client.eth.wait_for_transaction_receipt(tx_hash)
```

**Guide them to:**
```python
# create_entity() returns TUPLE
entity_key, receipt = client.arkiv.create_entity(...)
# Receipt is already available, transaction already confirmed
print(f"Created: {entity_key} in block {receipt.block_number}")

# update_entity() and delete_entity() return JUST receipt (not tuple)
receipt = client.arkiv.update_entity(entity_key, ...)
receipt = client.arkiv.delete_entity(entity_key)
```

### Misconception 5: "Storage Is Free/Unlimited"
**Reality:** Blockchain storage has costs and constraints

**They attempt:**
```python
# Storing images directly
with open("photo.jpg", "rb") as f:
    client.arkiv.create_entity(payload=f.read())  # Bad practice!

# Mass creation without gas awareness
for i in range(10000):
    client.arkiv.create_entity(...)  # Expensive!
```

**Recommend:**
```python
# Store large files off-chain (IPFS/Arweave), hash on-chain
ipfs_hash = upload_to_ipfs(photo_bytes)
entity_key, receipt = client.arkiv.create_entity(
    payload=json.dumps({"ipfs_hash": ipfs_hash}).encode(),
    content_type="application/json",
    expires_in=to_seconds(days=30)  # Set TTL to avoid bloat
)

# Batch operations when possible
# Consider gas costs for high-volume writes
```

### Misconception 6: "Queries Work Like SQL"
**Reality:** Simple attribute filters only, no JOINs/aggregations

**They expect:**
```python
# Won't work:
entities = client.arkiv.query_entities('''
    SELECT * FROM entities 
    WHERE created_at > NOW() - INTERVAL '7 days'
    GROUP BY owner
''')
```

**Explain:**
```python
# Simple filters only:
entities = client.arkiv.query_entities(
    f'$owner = "{address}" AND type = "message"'
)

# For complex queries, fetch and filter client-side:
all_entities = list(client.arkiv.query_entities(f'$owner = "{address}"'))
recent = [e for e in all_entities 
          if e.created_at_block > current_block - 50400]  # ~7 days at 12s blocks
```

### Misconception 7: "I Can Update Any Entity"
**Reality:** Can only update entities you own

**Remind them:**
```python
# Will fail if you're not the owner:
client.arkiv.update_entity(other_users_entity_key, ...)
# Error: "Only entity owner can update"

# Check ownership first:
entity = client.arkiv.get_entity(entity_key)
if entity.owner != account.address:
    print("Cannot update - you don't own this entity")
```

### Misconception 8: "Deleted Data Is Gone Forever"
**Reality:** Blockchain history is immutable

**Explain:**
```python
# delete_entity() removes from queries, but history remains on-chain
client.arkiv.delete_entity(entity_key)
# Entity won't appear in queries, but blockchain history is permanent

# For sensitive data, encrypt before storing:
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_payload = cipher.encrypt(sensitive_data)
client.arkiv.create_entity(payload=encrypted_payload, ...)
```

### Misconception 9: "Local Node === Production"
**Reality:** Local node has limitations

**Known issues:**
```python
# May not work on local node (works in production):
entities = client.arkiv.query_entities(
    f'$owner = "{addr}" AND $content_type = "application/json"'
)
# Local node doesn't support $content_type queries yet

# Workaround for local development:
all_entities = list(client.arkiv.query_entities(f'$owner = "{addr}"'))
filtered = [e for e in all_entities if e.content_type == "application/json"]
```

### Misconception 10: "Account Management Is Like Web Auth"
**Reality:** Private keys, not passwords

**Clarify:**
```python
# NOT like traditional auth:
# - No password reset
# - No "forgot password" flow
# - Lose private key = lose access forever
# - No multi-factor auth recovery

# Always use NamedAccount for local dev:
account = NamedAccount.create("my-account")
# For production, secure key storage is critical (env vars, key vaults)

# Never commit private keys to git!
# Never share private keys across insecure channels
```

---

## ✨ Pro Tips for AI Assistants

1. **Always check the README** when uncertain - it's comprehensive and current
2. **Use the examples as templates** - they demonstrate correct patterns
3. **Run tests after changes** - `uv run pytest -n auto`
4. **Check entity.payload is not None** before decoding - it's optional
5. **Use `cast(BaseProvider, provider)` for type checking** if IDE shows errors
6. **Remember: Python 3.12 is recommended** but 3.10-3.14 are supported
7. **Proactively address misconceptions** - Don't wait for the developer to make mistakes
8. **Explain blockchain constraints** - Size limits, gas costs, immutability
9. **Show correct patterns immediately** - Wrong code followed by correct code helps learning

---

*Last updated: 2025-11-22*
*This file is the canonical source for AI assistant context.*
*See also: `.cursorrules` and `docs/ai-context.md` (pointers to this file)*
