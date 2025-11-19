# Arkiv Python Starter

**Get started with Arkiv in under 2 minutes!** 🚀

This starter template provides everything you need to build applications with the Arkiv SDK for Python. No complex setup required—just clone, open, and run.

## What is Arkiv?

Arkiv is Web3 database that solves the Web3 data trilemma.
Store, query, and manage data on-chain with the simplicity of a traditional database, but with blockchain guarantees.

**Key Features:**
- 📦 **On-chain Storage** - Data lives on the blockchain, not centralized servers
- 🔍 **Rich Queries** - Filter, sort, and paginate like a traditional database
- ⚡ **Real-time Events** - Subscribe to data changes as they happen
- 🔗 **Web3 Compatible** - Just a simple extension of the web3.py library

## Prerequisites

You should already have:
- ✅ Git
- ✅ Docker
- ✅ VS Code
- ✅ GitHub Copilot (optional but recommended)

**Python Version:** This template uses **Python 3.12** for optimal compatibility. The Arkiv SDK supports Python 3.10-3.14, but we recommend 3.12 because:
- **Broad package compatibility** - Most Python packages have pre-built wheels
- **Stable and mature** - Well-tested in production environments  
- **Modern features** - Includes recent Python improvements
- **Long-term support** - Maintained until October 2028

If you need a different Python version (3.10, 3.11, 3.13, or 3.14), edit `.python-version` and rebuild the container.

## Quick Start

### 1. Clone and Open

```bash
git clone <your-repo-url>
cd arkiv-python-starter
code .
```

### 2. Reopen in Dev Container

When VS Code prompts you, click **"Reopen in Container"** (or use Command Palette: `Dev Containers: Reopen in Container`)

The dev container will:
- Install Python 3.12
- Set up Docker-in-Docker for local Arkiv nodes
- Install the Arkiv SDK and dependencies
- Configure your Python environment

**This takes 1-2 minutes on first run.**

### 3. Run Your First Example

```bash
uv run python -m arkiv_starter.01_basic_crud
```

You should see output like:
```
🚀 Starting local Arkiv node...
✅ Node running at http://127.0.0.1:...
💰 Created account: 0x...
✅ Account funded with 1000000000000000000 wei
📝 Creating entity...
✅ Entity created! Transaction: 0x...
📦 Entity ID: 1
...
```

**That's it!** You're now running Arkiv locally and performing CRUD operations on-chain.

## ⚠️ Naming Convention Quick Reference

**Before you start coding, understand these naming conventions:**

| Context | Convention | Examples |
|---------|-----------|----------|
| **Python SDK** | snake_case | `entity_key`, `content_type`, `from_block`, `expires_in` |
| **Query Syntax** | snake_case with `$` | `$owner`, `$content_type`, `$created_at` |
| **Contract Events** | camelCase | `entityKey`, `ownerAddress`, `expirationBlock` |
| **Entity Attributes** | snake_case | `entity.key`, `entity.payload`, `entity.expires_at_block` |

**Common mistakes to avoid:**
- ❌ `$contentType` → ✅ `$content_type` (in queries)
- ❌ `entity.id` → ✅ `entity.key` (attribute changed)
- ❌ `entity.content` → ✅ `entity.payload` (attribute changed)
- ❌ `event['args']['entity_key']` → ✅ `event['args']['entityKey']` (events are camelCase)

See [API_REFERENCE.md](API_REFERENCE.md#️-important-naming-conventions) for detailed examples.

## Understanding Entities

In Arkiv, **entities** are the fundamental units of data storage.
Think of them as records in a database, but stored on-chain with blockchain guarantees.

### Entity Components

Every entity has three core components:

#### 1. Payload (Content)
The actual data you want to store on-chain.

- **Type:** Raw bytes (`bytes` in Python)
- **Size:** Up to approx 100KB per entity
- **Format:** Can be anything—text, JSON, binary data, serialized objects
- **Example:**
  ```python
  # Text data
  payload = b"Hello, Arkiv!"

  # JSON data
  import json
  payload = json.dumps({"name": "Alice", "age": 30}).encode()

  # Binary data (e.g., small image)
  with open("icon.png", "rb") as f:
      payload = f.read()
  ```

#### 2. Attributes (Metadata)
Descriptive information about the entity that enables querying and filtering.

Arkiv supports two types of attributes:

##### Arkiv-Controlled Attributes (System)
These are automatically managed by Arkiv and prefixed with `$` in queries:

- **`$key`:** Unique entity identifier assigned on creation (automatically set)
- **`$owner`:** Ethereum address of the entity creator (automatically set)
- **`$content_type`:** MIME type describing the payload format (⚠️ snake_case in queries!)
- **`$created_at` / `$updated_at`:** Blockchain block numbers tracking lifecycle (automatically set)
- **`$expires_at`:** Block number when the entity expires (calculated from `expires_in`)

⚠️ **Note:** In Python code, use `content_type` parameter (snake_case). In queries, use `$content_type` (snake_case with `$`).

You **cannot** create custom attributes with the `$` prefix—these are reserved for Arkiv's internal use.

##### User-Controlled Attributes (Custom)
These are defined by your application and enable domain-specific queries:

- **No `$` prefix** - Use any name without the dollar sign
- **Examples:** `type`, `category`, `status`, `userId`, `priority`, etc.
- **Purpose:** Enable filtering and sorting based on your business logic

**Example:**
```python
# Creating an entity with custom attributes (Python SDK uses snake_case)
entity_key, receipt = client.arkiv.create_entity(
    payload=b"User profile data",
    content_type="application/json",  # Python parameter: snake_case
    expires_in=86400,
    attributes={
        "type": "user_profile",      # Custom attribute
        "userId": "alice123",         # Custom attribute
        "status": "active"            # Custom attribute
    }
)

# Querying by Arkiv-controlled attributes (query syntax uses $content_type)
entities = list(client.arkiv.query_entities(
    f'$owner = "0x1234..." AND $content_type = "application/json"'  # Query: snake_case with $
))

# Querying by user-controlled attributes
entities = list(client.arkiv.query_entities(
    'type = "user_profile" AND status = "active"'
))
```

#### 3. Expires In (TTL - Time To Live)
How long the entity should persist on-chain before automatic expiration.

- **Type:** Duration in seconds
- **Purpose:** Optimize blockchain storage and costs
- **Behavior:** After expiration, the entity is automatically removed
- **Default:** No default, needs to be set explicitly by user
- **Example:**
  ```python
  # Short-lived data (1 hour)
  client.arkiv.create_entity(payload=data, expires_in=client.arkiv.to_seconds(hours=1))

  # Longer storage (2 months)
  client.arkiv.create_entity(payload=data, expires_in=client.arkiv.to_seconds(days=60))

  # Using time utilities
  from arkiv import to_seconds
  client.arkiv.create_entity(
      payload=data,
      expires_in=to_seconds(hours=2, minutes=30)  # 2.5 hours
  )
  ```

### Why These Components Matter

- **Payload:** Your actual data, flexible and unopinionated
- **Attributes:** Enable powerful queries without indexing off-chain
- **Expires In:** Keeps blockchain lean and costs predictable

This design gives you the flexibility of a document database with the immutability and transparency of blockchain storage.

## Examples Overview

The `examples/` directory contains 4 progressive tutorials:

### Example 1: Basic CRUD Operations (5 min)
**File:** `01_basic_crud.py`

Learn the fundamentals:
- Creating entities (storing data on-chain)
- Reading entities by ID
- Updating existing entities
- Deleting entities

**Run it:**
```bash
uv run python -m arkiv_starter.01_basic_crud
```

### Example 2: Querying Entities (5 min)
**File:** `02_queries.py`

Master data retrieval:
- Query by owner
- Filter by content type
- Sort results
- Paginate large result sets

**Run it:**
```bash
uv run python -m arkiv_starter.02_queries
```

### Example 3: Blockchain Events (10 min)
**File:** `03_events.py`

Real-time data monitoring:
- Subscribe to entity lifecycle events
- Process event data
- Query historical events

**Run it:**
```bash
uv run python -m arkiv_starter.03_events
```

### Example 4: Web3 Integration (10 min)
**File:** `04_web3_integration.py`

Advanced usage:
- Mix Arkiv with standard web3.py calls
- Direct contract interaction
- Manual transaction signing
- Full control when you need it

**Run it:**
```bash
uv run python -m arkiv_starter.04_web3_integration
```

## Project Structure

```
arkiv-python-starter/
├── .devcontainer/
│   ├── devcontainer.json       # Dev container configuration
│   └── post-create.sh          # Setup script
├── .vscode/
│   └── settings.json           # Python/Pylance settings
├── src/
│   └── arkiv_starter/
│       ├── 01_basic_crud.py        # CRUD operations
│       ├── 02_queries.py           # Filtering and sorting
│       ├── 03_events.py            # Event listening
│       └── 04_web3_integration.py  # Web3 compatibility
├── tests/
│   ├── conftest.py             # Test configuration
│   ├── test_01_basic_crud.py   # CRUD tests
│   ├── test_02_queries.py      # Query tests
│   └── test_utilities.py       # Utility function tests
├── .gitignore
├── API_REFERENCE.md            # Complete API documentation
├── README.md                   # This file
├── pyproject.toml              # Project dependencies
└── uv.lock                     # Locked dependencies (auto-generated)
```

## Project Structure

This template follows the **src-layout** pattern, which is the modern Python standard:

- **`src/arkiv_starter/`** - Your application code goes here (currently contains numbered examples)
- **`tests/`** - Test files that mirror the src structure
- **`.devcontainer/`** - Dev container configuration for consistent development
- **`.vscode/`** - VS Code settings optimized for Python

**Why src-layout?**
- ✅ Prevents accidental imports of uninstalled code
- ✅ Matches the structure of published Python packages
- ✅ Clear separation between source code and tooling
- ✅ Standard practice in modern Python projects

**To start building your app:**
Replace the numbered example files with your own modules, or keep them as reference and create new files alongside them.

## How It Works

Each example:
1. **Starts a local Arkiv node** - Runs in Docker, no external dependencies
2. **Creates and funds a test account** - Ready to transact immediately
3. **Demonstrates specific features** - Focused, runnable code
4. **Cleans up automatically** - Stops the node when done

All examples are self-contained and can run independently as modules: `uv run python -m arkiv_starter.01_basic_crud`

## Common Pitfalls for AI Agents

When using AI assistants like GitHub Copilot or Claude to work with this codebase:

### ❌ Wrong Naming Convention
```python
# ❌ DON'T: Mixing camelCase in Python code
result = client.arkiv.query_entities_page(
    f'$owner = "{addr}" AND $contentType = "text/plain"'  # Wrong!
)
entity_key = event['args']['entity_key']  # Wrong!

# ✅ DO: Use correct conventions
result = client.arkiv.query_entities_page(
    f'$owner = "{addr}" AND $content_type = "text/plain"'  # Correct: snake_case
)
entity_key = hex(event['args']['entityKey'])  # Correct: camelCase in events
```

### ❌ Wrong Return Value Unpacking
```python
# ❌ DON'T: Old API style
tx_hash = client.arkiv.create_entity(...)  # Returns tuple now!
receipt = client.eth.wait_for_transaction_receipt(tx_hash)  # Won't work

# ✅ DO: Unpack correctly
entity_key, receipt = client.arkiv.create_entity(...)  # Returns (key, receipt)
receipt = client.arkiv.update_entity(...)  # Returns just receipt
```

### ❌ Wrong Entity Attributes
```python
# ❌ DON'T: Old attribute names
print(entity.id)  # Wrong attribute name
print(entity.content)  # Wrong attribute name

# ✅ DO: Current attribute names
print(entity.key)  # Correct
print(entity.payload)  # Correct
```

**When in doubt, check [API_REFERENCE.md](API_REFERENCE.md) for the authoritative API documentation.**

## Using GitHub Copilot

This template is optimized for GitHub Copilot:

- 📝 **Well-commented examples** - Copilot learns from clear explanations
- 🎯 **Focused code patterns** - Each example teaches specific concepts
- 💬 **Natural language prompts** - Ask Copilot to modify examples

**Try asking Copilot:**
- "Create an entity that stores JSON data using the correct snake_case convention"
- "Query entities by owner and content_type"
- "Listen to ArkivEntityCreated events and extract the entityKey"

## Common Tasks

### Install Additional Dependencies

```bash
uv add <package-name>
```

### Run Python REPL with Arkiv

```bash
uv run ipython
```

Then in IPython:
```python
from arkiv import Arkiv
from arkiv.node import ArkivNode
# ... experiment interactively
```

### Check Arkiv SDK Version

```bash
uv run python -c "import arkiv; print(arkiv.__version__)"
```

### Run Tests

The starter includes automated tests you can run:

```bash
uv run pytest
```

This runs tests that verify:
- ✅ Basic CRUD operations work correctly
- ✅ Query functionality performs as expected
- ✅ Utility functions produce correct results
- ✅ Field masks work for selective retrieval

Tests use a local Arkiv node and run automatically - no configuration needed!

## Deploying to Production

Once you've mastered local development, connect to the Mendoza testnet:

### Mendoza Testnet Connection

```python
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder

# Configure provider for Mendoza testnet
provider = ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc").build()

# Load your account (create one if you don't have it)
account = NamedAccount.from_private_key("my-account", "0x...")
# Or from wallet file:
# with open('wallet.json') as f:
#     account = NamedAccount.from_wallet("my-account", f.read(), "password")

# Initialize client
client = Arkiv(provider=provider, account=account)

# Now use normally - same API as local development!
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Hello from Mendoza!",
    content_type="text/plain",
    attributes={"env": "testnet"},
    expires_in=client.arkiv.to_seconds(days=7)
)
```

### Key Differences: Local vs. Testnet

| Aspect | Local Development | Mendoza Testnet |
|--------|------------------|-----------------|
| **Provider** | `ProviderBuilder().node()` | `ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc")` |
| **Account Funding** | `node.fund_account()` | Request from faucet (Discord) |
| **Data Persistence** | Lost when node stops | Permanent on testnet |
| **Block Time** | ~1-2 seconds | ~2 seconds |
| **Network Access** | Local only | Public internet |

### Environment Variables Pattern

For production apps, use environment variables:

```python
import os
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder

# Configure from environment
RPC_URL = os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc")
PRIVATE_KEY = os.getenv("ARKIV_PRIVATE_KEY")

provider = ProviderBuilder().custom(RPC_URL).build()
account = NamedAccount.from_private_key("app", PRIVATE_KEY)
client = Arkiv(provider=provider, account=account)
```

### Getting Testnet Funds

To use Mendoza testnet, you need test tokens:

1. **Create an account**:
   ```python
   account = NamedAccount.create("my-testnet-account")
   print(f"Address: {account.address}")
   ```

2. **Request funds**: Join [Discord](https://discord.gg/arkiv) and request testnet tokens for your address

3. **Verify balance**:
   ```python
   balance = client.eth.get_balance(account.address)
   print(f"Balance: {balance / 10**18} ETH")
   ```

## Next Steps

Once you've run all examples:

1. **Modify the examples** - Change payloads, filters, or operations
2. **Build your application** - Use these patterns in your own code
3. **Deploy to testnet** - Follow the production guide above
4. **Read the API reference** - See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation
5. **Join the community** - Get help and share your projects on Discord

## Troubleshooting

### Dev Container Won't Start

**Problem:** Docker issues or container build failures

**Solution:**
- Ensure Docker is running
- Try: `Dev Containers: Rebuild Container` from Command Palette

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'arkiv'` or red import lines in IDE

**Solution:**
```bash
uv sync
```

Then in VS Code, press `Ctrl+Shift+P` and select "Python: Select Interpreter" → choose `.venv`

### Python Version Issues

**Problem:** Need a different Python version

**Solution:**
1. Edit `.python-version` (e.g., change `3.12` to `3.11` or `3.13`)
2. Rebuild container: `Dev Containers: Rebuild Container`
3. Arkiv SDK supports Python 3.10-3.14

### Node Connection Errors

**Problem:** Can't connect to Arkiv node

**Solution:**
- Check Docker is running: `docker ps`
- The examples start nodes automatically—wait for the "Node running" message

### Examples Run Slowly

**Problem:** Operations take a long time

**Solution:**
- First run downloads Docker images (one-time delay)
- Subsequent runs are much faster
- Local nodes are slower than production—this is expected

## Contributing

Found a bug or have a suggestion? Please open an issue or submit a PR!

## Resources

- 📚 [Arkiv Documentation](https://docs.arkiv.network)
- 🐍 [Python SDK Reference](https://github.com/Arkiv-Network/arkiv-sdk-python)
- 💬 [Discord Community](https://discord.gg/arkiv)
- 🐦 [Twitter/X](https://twitter.com/ArkivNetwork)

## License

MIT License - See LICENSE file for details

---

**Happy building with Arkiv! 🚀**
