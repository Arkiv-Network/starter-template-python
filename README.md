# Arkiv Python Starter

**Get started with Arkiv in under 2 minutes!** 🚀

This starter template provides everything you need to build applications with the Arkiv SDK for Python. No complex setup required—just clone, open, and run.

## Table of Contents

- [What is Arkiv?](#what-is-arkiv)
- [Quick Start](#quick-start)
- [Understanding Entities](#understanding-entities)
- [Examples](#examples)
- [Working with AI Assistants](#working-with-ai-assistants)
- [Development Guide](#development-guide)
  - [Project Structure](#project-structure)
  - [Naming Conventions](#naming-conventions)
  - [Common Tasks](#common-tasks)
  - [Troubleshooting](#troubleshooting)
- [Deploying to Production](#deploying-to-production)
- [Resources](#resources)

---

## What is Arkiv?

Arkiv is a Web3 database that solves the Web3 data trilemma.
Store, query, and manage data on-chain with the simplicity of a traditional database, but with blockchain guarantees.

**Key Features:**
- 📦 **On-chain Storage** - Data lives on the blockchain, not centralized servers
- 🔍 **Rich Queries** - Filter, sort, and paginate like a traditional database
- ⚡ **Real-time Events** - Subscribe to data changes as they happen
- 🔗 **Web3 Compatible** - Just a simple extension of the web3.py library

**Prerequisites:**
- ✅ Git
- ✅ Docker
- ✅ VS Code
- ✅ GitHub Copilot (optional but recommended)

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
- Install Python 3.12 (supports 3.10-3.14, optimized for broad compatibility)
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

## Examples

The template includes 4 progressive tutorials, each building on the previous:

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



## How It Works

Each example:
1. **Starts a local Arkiv node** - Runs in Docker, no external dependencies
2. **Creates and funds a test account** - Ready to transact immediately
3. **Demonstrates specific features** - Focused, runnable code
4. **Cleans up automatically** - Stops the node when done

All examples are self-contained and can run independently as modules: `uv run python -m arkiv_starter.01_basic_crud`

---

## Working with AI Assistants

This template is designed to work seamlessly with AI coding assistants like **GitHub Copilot**, **Claude**, and **ChatGPT**.

### 🤖 For AI Agents: Critical Context

If you're an AI assistant helping with this codebase, prioritize these facts:

**1. Naming Conventions (Most Common Mistake)**

| Context | Convention | Examples |
|---------|-----------|----------|
| **Python SDK** | snake_case | `entity_key`, `content_type`, `from_block`, `expires_in` |
| **Query Syntax** | snake_case with `$` | `$owner`, `$content_type`, `$created_at` |
| **Contract Events** | camelCase | `entityKey`, `ownerAddress`, `expirationBlock` |
| **Entity Attributes** | snake_case | `entity.key`, `entity.payload`, `entity.expires_at_block` |

**2. API Return Values**
```python
# create_entity returns a TUPLE:
entity_key, receipt = client.arkiv.create_entity(...)

# update/delete return just receipt:
receipt = client.arkiv.update_entity(...)
receipt = client.arkiv.delete_entity(...)
```

**3. Current API (Not Old Versions)**
```python
# ✅ CORRECT (current API)
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder  # Singular: provider

account = NamedAccount.create("name")  # Not Account.create()
entity.key      # Not entity.id
entity.payload  # Not entity.content
event['args']['entityKey']  # camelCase in events
```

**4. Module Structure**
- Examples live in `src/arkiv_starter/` (not `examples/`)
- Run as modules: `uv run python -m arkiv_starter.01_basic_crud`
- Python 3.12 recommended (supports 3.10-3.14)

**Common AI Mistakes to Avoid:**

❌ **Wrong:**
```python
# Mixing camelCase in queries
f'$contentType = "text/plain"'  # WRONG
event['args']['entity_key']     # WRONG
entity.id                        # WRONG
```

✅ **Correct:**
```python
# Use snake_case in queries
f'$content_type = "text/plain"'  # CORRECT
hex(event['args']['entityKey'])  # CORRECT (camelCase in events)
entity.key                        # CORRECT
```

**When in doubt, check [API_REFERENCE.md](API_REFERENCE.md) first.**

### 💬 Using GitHub Copilot

This template is optimized for interactive AI assistance:

- 📝 **Well-commented examples** - Clear patterns for learning
- 🎯 **Focused code** - Each example teaches specific concepts
- 💬 **Natural language prompts** - Ask Copilot to help

**Try asking Copilot:**
- "Create an entity that stores JSON data"
- "Query entities by owner and content_type"
- "Listen to ArkivEntityCreated events and extract the entityKey"
- "Update an entity's payload and wait for confirmation"

---

## Development Guide

### Project Structure

This template follows the **src-layout** pattern (modern Python standard):

```
arkiv-python-starter/
├── src/
│   └── arkiv_starter/          # Your application code
│       ├── 01_basic_crud.py
│       ├── 02_queries.py
│       ├── 03_events.py
│       └── 04_web3_integration.py
├── tests/                      # Test files
│   ├── conftest.py
│   ├── test_01_basic_crud.py
│   └── test_02_queries.py
├── .devcontainer/              # Dev container config
├── .vscode/                    # VS Code settings
├── pyproject.toml              # Dependencies & tools
└── .python-version             # Python version (3.12)
```

**Why src-layout?**
- ✅ Prevents accidental imports of uninstalled code
- ✅ Matches published Python package structure
- ✅ Clear separation between source and tooling
- ✅ Industry standard for modern Python projects

**To build your app:** Replace or extend the numbered examples with your own modules.

### Naming Conventions

Arkiv uses **three different naming conventions** depending on context:

#### Python SDK → snake_case
```python
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    content_type="text/plain",
    expires_in=3600,
    attributes={"user_id": "123"}
)
```

#### Query Syntax → snake_case with `$`
```python
# System attributes with $ prefix
entities = list(client.arkiv.query_entities(
    f'$owner = "{address}" AND $content_type = "application/json"'
))

# User attributes without $ prefix
entities = list(client.arkiv.query_entities(
    'type = "user_profile" AND status = "active"'
))
```

#### Contract Events → camelCase
```python
event_filter = arkiv_contract.events.ArkivEntityCreated.create_filter(from_block="latest")
for event in event_filter.get_all_entries():
    entity_key = hex(event['args']['entityKey'])      # camelCase!
    owner = event['args']['ownerAddress']             # camelCase!
    expiration = event['args']['expirationBlock']     # camelCase!
```

#### Entity Attributes → snake_case
```python
print(entity.key)              # Not entity.id
print(entity.payload)          # Not entity.content
print(entity.owner)
print(entity.content_type)
print(entity.expires_at_block)
print(entity.created_at_block)
```

**Why three conventions?**
- Python SDK follows Python naming standards (PEP 8)
- Query syntax prioritizes readability and SQL-like familiarity
- Contract events follow Solidity conventions (cannot be changed)

See [API_REFERENCE.md](API_REFERENCE.md#️-important-naming-conventions) for complete details.

### Common Tasks

#### Install Additional Dependencies

```bash
uv add <package-name>
```

#### Run Python REPL with Arkiv

```bash
uv run ipython
```

Then in IPython:
```python
from arkiv import Arkiv
from arkiv.node import ArkivNode
# ... experiment interactively
```

#### Check Arkiv SDK Version

```bash
uv run python -c "import arkiv; print(arkiv.__version__)"
```

#### Run Tests

The starter includes automated tests:

```bash
uv run pytest
```

This verifies:
- ✅ Basic CRUD operations work correctly
- ✅ Query functionality performs as expected
- ✅ Utility functions produce correct results
- ✅ Field masks work for selective retrieval

Tests use a local Arkiv node and run automatically - no configuration needed!

#### Change Python Version

The template uses Python 3.12 by default (recommended for compatibility). To use a different version:

1. Edit `.python-version` (e.g., change to `3.11`, `3.13`, or `3.14`)
2. Rebuild container: Command Palette → `Dev Containers: Rebuild Container`
3. UV will automatically install the specified Python version

**Why Python 3.12?**
- Broad package compatibility (most wheels available)
- Stable and well-tested in production
- Long-term support until October 2028
- Modern features without bleeding-edge risks

### Troubleshooting

#### Dev Container Won't Start

**Problem:** Docker issues or container build failures

**Solution:**
- Ensure Docker is running: `docker ps`
- Try rebuilding: Command Palette → `Dev Containers: Rebuild Container`

#### Import Errors in IDE

**Problem:** Red import lines or `ModuleNotFoundError`

**Solution:**
```bash
uv sync
```

Then: `Ctrl+Shift+P` → `Python: Select Interpreter` → choose `.venv`

#### Node Connection Errors

**Problem:** Can't connect to Arkiv node

**Solution:**
- Check Docker: `docker ps`
- Examples start nodes automatically—wait for "Node running" message
- First run downloads Docker images (one-time delay)

#### Examples Run Slowly

**Problem:** Operations take a long time

**Solution:**
- First run downloads images (one-time)
- Subsequent runs are faster
- Local nodes are slower than production (expected)

---

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

---

- 🐍 [Arkiv Getting Started](hhttps://arkiv.network/getting-started/python)
- 🐍 [Arkiv SDK for Python on Github](https://github.com/Arkiv-Network/arkiv-sdk-python)
- 📖 [API_REFERENCE.md](API_REFERENCE.md) - Local API reference with examples
- 💬 [Discord Community](https://discord.gg/arkiv) - Get help and share projects
- 🐦 [Twitter/X](https://twitter.com/ArkivNetwork) - Latest updates and announcements

## Next Steps

Once you've completed the examples:

1. **Experiment** - Modify examples to understand the API
2. **Build** - Create your own application using these patterns
3. **Deploy** - Move to Mendoza testnet when ready
4. **Share** - Join Discord and show the community what you've built

## Contributing

Found a bug or have a suggestion? Please open an issue or submit a PR!

## License

MIT License - See LICENSE file for details

---

**Happy building with Arkiv! 🚀**
