# Arkiv SDK API Reference

Complete reference for the Arkiv Python SDK.

## ⚠️ Important: Naming Conventions

The Arkiv SDK uses **different naming conventions** in different contexts. Understanding these is critical:

### Python SDK (snake_case)
All Python SDK methods, parameters, and object attributes use **snake_case**:
- ✅ `entity_key` (not entityKey)
- ✅ `content_type` (not contentType)
- ✅ `from_block` (not fromBlock)
- ✅ `to_block` (not toBlock)
- ✅ `expires_in` (not expiresIn)

### Query Syntax (snake_case with $ prefix)
Arkiv-controlled attributes in queries use **snake_case with `$` prefix**:
- ✅ `$owner` - Entity owner address
- ✅ `$key` - Entity key
- ✅ `$content_type` - MIME type (note: snake_case, not camelCase)
- ✅ `$created_at` - Creation block
- ✅ `$expires_at` - Expiration block

### Smart Contract Events (camelCase)
Blockchain event arguments use **camelCase** (Solidity convention):
- ✅ `entityKey` (not entity_key)
- ✅ `ownerAddress` (not owner_address)
- ✅ `expirationBlock` (not expiration_block)
- Event names: `ArkivEntityCreated`, `ArkivEntityUpdated`, `ArkivEntityDeleted`

### Entity Object Attributes (snake_case)
Entity objects returned from queries use **snake_case**:
- ✅ `entity.key` (not entity.id)
- ✅ `entity.payload` (not entity.content)
- ✅ `entity.content_type`
- ✅ `entity.expires_at_block`
- ✅ `entity.created_at_block`

**Example showing all conventions:**
```python
# Creating entity (Python SDK - snake_case)
entity_key, receipt = client.arkiv.create_entity(
    payload=b"data",
    content_type="text/plain",  # snake_case
    expires_in=3600
)

# Querying (Query syntax - snake_case with $)
for entity in client.arkiv.query_entities(f'$owner = "{account.address}" AND $content_type = "text/plain"'):
    print(entity.payload)  # Entity attributes - snake_case

# Event listening (Contract events - camelCase)
filter = contract.events.ArkivEntityCreated.create_filter(from_block="latest")  # from_block is snake_case
for event in filter.get_new_entries():
    print(event['args']['entityKey'])  # Event args - camelCase
    print(event['args']['ownerAddress'])  # Event args - camelCase
```

---

## Table of Contents

1. [Client Initialization](#client-initialization)
2. [Entity Operations](#entity-operations)
3. [Querying](#querying)
4. [Events](#events)
5. [Provider Configuration](#provider-configuration)
6. [Account Management](#account-management)
7. [Type Reference](#type-reference)
8. [Utilities](#utilities)

---

## Client Initialization

### `Arkiv(provider, account=None, **kwargs)`

Main client class that extends Web3 with entity management.

**Parameters:**
- `provider` (BaseProvider | None): Web3 provider instance. If None, creates local ArkivNode with default account
- `account` (NamedAccount | LocalAccount | None): Optional account to use as default signer
- `**kwargs`: Additional arguments passed to Web3 constructor

**Returns:** `Arkiv` client instance

**Examples:**
```python
# Auto-managed local node with default account
with Arkiv() as client:
    print(client.eth.default_account)

# Custom provider and account
from arkiv.provider import ProviderBuilder
provider = ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc").build()
account = NamedAccount.from_private_key("alice", "0x...")
client = Arkiv(provider=provider, account=account)
```

### `AsyncArkiv(provider, account=None, **kwargs)`

Async version of Arkiv client for use with asyncio.

**Parameters:** Same as `Arkiv`

**Usage:**
```python
async with AsyncArkiv(provider, account) as client:
    entity_key, receipt = await client.arkiv.create_entity(payload=b"Hello")
```

---

## Entity Operations

All entity operations are accessed through `client.arkiv.*` methods.

### `create_entity(payload=None, content_type=None, attributes=None, expires_in=None, tx_params=None)`

Create a new entity on-chain.

**Parameters:**
- `payload` (bytes | None): Data to store (default: empty bytes)
- `content_type` (str | None): MIME type (default: "application/octet-stream")
- `attributes` (Attributes | None): Key-value metadata (default: empty dict)
- `expires_in` (int | None): Lifetime in **seconds** (required)
- `tx_params` (TxParams | None): Optional transaction parameters (gas, gasPrice, etc.)

**Returns:** `tuple[EntityKey, TransactionReceipt]`
- `EntityKey`: Unique identifier for the created entity
- `TransactionReceipt`: Transaction details and events

**Raises:**
- `RuntimeError`: If transaction fails
- `ValueError`: If invalid parameters provided

**Example:**
```python
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Hello, Arkiv!",
    content_type="text/plain",
    attributes={"type": "greeting", "version": 1},
    expires_in=client.arkiv.to_seconds(hours=24)
)
print(f"Created: {entity_key}")
print(f"Block: {receipt.block_number}")
```

### `get_entity(entity_key, fields=ALL, at_block=None)`

Retrieve an entity by its key.

**Parameters:**
- `entity_key` (EntityKey): The entity key to retrieve
- `fields` (int): Bitfield indicating which fields to retrieve (default: ALL)
- `at_block` (int | None): Block number to query at (default: latest)

**Field Constants:** (from `arkiv.types`)
- `KEY` - Entity key
- `ATTRIBUTES` - Custom attributes
- `PAYLOAD` - Content data
- `CONTENT_TYPE` - MIME type
- `EXPIRATION` - Expiration block
- `OWNER` - Owner address
- `CREATED_AT` - Creation block
- `LAST_MODIFIED_AT` - Last update block
- `ALL` - All fields

**Returns:** `Entity` object

**Raises:** `ValueError` if entity not found

**Example:**
```python
# Get all fields
entity = client.arkiv.get_entity(entity_key)
print(f"Owner: {entity.owner}")
print(f"Payload: {entity.payload.decode('utf-8')}")

# Get only specific fields for efficiency
from arkiv.types import PAYLOAD, ATTRIBUTES
entity = client.arkiv.get_entity(entity_key, fields=PAYLOAD | ATTRIBUTES)
```

### `update_entity(entity_key, payload=None, content_type=None, attributes=None, expires_in=None, tx_params=None)`

Update an existing entity. **Replaces all fields** (not a merge).

**Parameters:**
- `entity_key` (EntityKey): The entity to update
- `payload` (bytes | None): New payload (default: empty bytes)
- `content_type` (str | None): New content type (default: "application/octet-stream")
- `attributes` (Attributes | None): New attributes (default: empty dict)
- `expires_in` (int | None): New expiration in **seconds**
- `tx_params` (TxParams | None): Optional transaction parameters

**Returns:** `TransactionReceipt`

**Example:**
```python
receipt = client.arkiv.update_entity(
    entity_key=my_key,
    payload=b"Updated content",
    attributes={"status": "updated", "version": 2},
    expires_in=client.arkiv.to_seconds(hours=48)
)
```

### `extend_entity(entity_key, extend_by, tx_params=None)`

Extend an entity's lifetime.

**Parameters:**
- `entity_key` (EntityKey): Entity to extend
- `extend_by` (int): Number of **seconds** to add to expiration
- `tx_params` (TxParams | None): Optional transaction parameters

**Returns:** `TransactionReceipt`

**Example:**
```python
# Extend by 1 hour
receipt = client.arkiv.extend_entity(
    entity_key=my_key,
    extend_by=3600
)
```

### `change_owner(entity_key, new_owner, tx_params=None)`

Transfer ownership of an entity.

**Parameters:**
- `entity_key` (EntityKey): Entity to transfer
- `new_owner` (ChecksumAddress): New owner's Ethereum address
- `tx_params` (TxParams | None): Optional transaction parameters

**Returns:** `TransactionReceipt`

**Example:**
```python
receipt = client.arkiv.change_owner(
    entity_key=my_key,
    new_owner="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
)
```

### `delete_entity(entity_key, tx_params=None)`

Permanently delete an entity.

**Parameters:**
- `entity_key` (EntityKey): Entity to delete
- `tx_params` (TxParams | None): Optional transaction parameters

**Returns:** `TransactionReceipt`

**Example:**
```python
receipt = client.arkiv.delete_entity(entity_key=my_key)
```

### `entity_exists(entity_key, at_block=None)`

Check if an entity exists.

**Parameters:**
- `entity_key` (EntityKey): Entity key to check
- `at_block` (int | None): Block number to check at (default: latest)

**Returns:** `bool` - True if exists, False otherwise

**Example:**
```python
if client.arkiv.entity_exists(entity_key):
    print("Entity exists!")
```

### `execute(operations, tx_params=None)`

Execute multiple operations in a single transaction (batch).

**Parameters:**
- `operations` (Operations): Batch of operations to execute
- `tx_params` (TxParams | None): Optional transaction parameters

**Returns:** `TransactionReceipt` with results for all operations

**Example:**
```python
from arkiv.types import Operations, CreateOp, UpdateOp, DeleteOp

operations = Operations(
    creates=[
        CreateOp(payload=b"Entity 1", content_type="text/plain",
                 attributes={}, expires_in=3600),
        CreateOp(payload=b"Entity 2", content_type="text/plain",
                 attributes={}, expires_in=3600),
    ],
    updates=[UpdateOp(key=existing_key, payload=b"Updated",
                      content_type="text/plain", attributes={}, expires_in=3600)],
    deletes=[DeleteOp(key=old_key)]
)

receipt = client.arkiv.execute(operations)
print(f"Created: {len(receipt.creates)} entities")
print(f"Updated: {len(receipt.updates)} entities")
print(f"Deleted: {len(receipt.deletes)} entities")
```

---

## Querying

### `query_entities_page(query, options=QUERY_OPTIONS_DEFAULT)`

Execute a query against entity storage.

**Parameters:**
- `query` (str): SQL-like WHERE clause to filter entities
- `options` (QueryOptions): Query configuration
  - `fields` (int): Which fields to retrieve (default: ALL)
  - `at_block` (int | None): Block number to query at
  - `max_results_per_page` (int): Limit results (default: 20)
  - `cursor` (Cursor | None): For pagination

**Returns:** `QueryPage` containing:
- `entities` (list[Entity]): Matching entities
- `block_number` (int): Block where query executed
- `cursor` (Cursor | None): For next page

**Query Syntax:**
- Arkiv-controlled attributes use `$` prefix with **snake_case**: `$key`, `$owner`, `$content_type`
- User attributes: `type`, `status`, `userId`, etc. (your own naming convention)
- Operators: `=`, `!=`, `<`, `>`, `<=`, `>=`, `AND`, `OR`
- String values in quotes: `"value"`

**Arkiv System Attributes (all snake_case):**
- `$key` - Entity unique identifier
- `$owner` - Owner's Ethereum address
- `$content_type` - MIME type (⚠️ note: `$content_type`, not `$contentType`)
- `$created_at` - Block number when created
- `$expires_at` - Block number when expires

**Examples:**
```python
# Query by owner
result = client.arkiv.query_entities_page(
    f'$owner = "{client.eth.default_account}"'
)

# Query by content type (note: snake_case)
result = client.arkiv.query_entities_page(
    f'$owner = "{account.address}" AND $content_type = "text/plain"'
)

# Query by custom attributes
result = client.arkiv.query_entities_page(
    'type = "user" AND status = "active"'
)

# Query with specific fields and pagination
from arkiv.types import QueryOptions, PAYLOAD, ATTRIBUTES
result = client.arkiv.query_entities_page(
    'type = "document"',
    options=QueryOptions(
        fields=PAYLOAD | ATTRIBUTES,
        max_results_per_page=10
    )
)
```

### `query_entities(query, options=QUERY_OPTIONS_DEFAULT)`

Query and return iterator over all results (handles pagination automatically).

**Parameters:** Same as `query_entities_page`

**Returns:** `QueryIterator` - Iterator yielding Entity objects

**Example:**
```python
for entity in client.arkiv.query_entities('type = "log"'):
    print(f"Entity {entity.key}: {entity.payload}")
```

---

## Events

⚠️ **Important:** Smart contract event arguments use **camelCase** (Solidity convention), not snake_case.

### Listening to Raw Contract Events

For maximum control, access the contract directly:

```python
# Get the Arkiv contract
arkiv_contract = client.arkiv.contract

# Create event filters (⚠️ note: from_block is snake_case, but event args are camelCase)
created_filter = arkiv_contract.events.ArkivEntityCreated.create_filter(from_block="latest")
updated_filter = arkiv_contract.events.ArkivEntityUpdated.create_filter(from_block="latest")
deleted_filter = arkiv_contract.events.ArkivEntityDeleted.create_filter(from_block="latest")

# Get new events
for event in created_filter.get_new_entries():
    # ⚠️ Event args are camelCase
    entity_key = hex(event['args']['entityKey'])  # Not entity_key!
    owner = event['args']['ownerAddress']  # Not owner_address!
    expiration = event['args']['expirationBlock']  # Not expiration_block!
    print(f"Entity {entity_key} created by {owner}")

# Query historical events
all_events = arkiv_contract.events.ArkivEntityCreated.get_logs(
    from_block=0,  # from_block is snake_case
    to_block="latest",  # to_block is snake_case
    argument_filters={"ownerAddress": account.address}  # ownerAddress is camelCase!
)
```

### `watch_entity_created(callback, from_block="latest", auto_start=True)`

Watch for entity creation events (SDK wrapper with snake_case event objects).

**Parameters:**
- `callback` (CreateCallback): Function called for each event: `callback(event: CreateEvent, tx_hash: TxHash)`
- `from_block` (BlockIdentifier): Starting block (default: "latest")
- `auto_start` (bool): Start watching immediately (default: True)

**Returns:** `EventFilter`

**Example:**
```python
def on_created(event, tx_hash):
    # SDK event objects use snake_case
    print(f"Created entity {event.key} by {event.owner_address}")
    print(f"Expires at block: {event.expiration_block}")

filter = client.arkiv.watch_entity_created(on_created)

# Later, stop watching
client.arkiv.cleanup_filters()
```

### `watch_entity_updated(callback, from_block="latest", auto_start=True)`

Watch for entity update events.

**Callback receives:** `UpdateEvent` with fields:
- `key` (EntityKey)
- `owner_address` (ChecksumAddress)
- `old_expiration_block` (int)
- `new_expiration_block` (int)
- `cost` (int)

### `watch_entity_extended(callback, from_block="latest", auto_start=True)`

Watch for entity extension events.

**Callback receives:** `ExtendEvent` with fields:
- `key` (EntityKey)
- `owner_address` (ChecksumAddress)
- `old_expiration_block` (int)
- `new_expiration_block` (int)

### `watch_entity_deleted(callback, from_block="latest", auto_start=True)`

Watch for entity deletion events.

**Callback receives:** `DeleteEvent` with fields:
- `key` (EntityKey)
- `owner_address` (ChecksumAddress)

### `cleanup_filters()`

Stop all active event watchers and clean up resources.

**Example:**
```python
# Start multiple watchers
client.arkiv.watch_entity_created(on_created)
client.arkiv.watch_entity_updated(on_updated)
client.arkiv.watch_entity_deleted(on_deleted)

# Stop all watchers
client.arkiv.cleanup_filters()
```

---

## Provider Configuration

### `ProviderBuilder()`

Fluent builder for creating Web3 providers with Arkiv presets.

**Methods:**

#### `.localhost(port=None)`
Configure for localhost development node (default port: 8545).

```python
provider = ProviderBuilder().localhost().build()
provider = ProviderBuilder().localhost(9000).build()
```

#### `.custom(url)`
Configure with custom RPC URL.

```python
provider = ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc").build()
```

#### `.node(arkiv_node=None)`
Configure for local ArkivNode instance. Auto-creates and starts node if None.

```python
from arkiv.node import ArkivNode
node = ArkivNode()
provider = ProviderBuilder().node(node).build()

# Auto-create node
provider = ProviderBuilder().node().build()
```

#### `.http()`
Use HTTP transport (default).

```python
provider = ProviderBuilder().localhost().http().build()
```

#### `.ws()`
Use WebSocket transport (always async).

```python
provider = ProviderBuilder().localhost().ws().build()
```

#### `.async_mode(enabled=True)`
Enable async providers (AsyncHTTPProvider for HTTP transport).

```python
provider = ProviderBuilder().localhost().async_mode().build()
# Returns AsyncHTTPProvider
```

#### `.build()`
Build and return the configured provider.

**Returns:**
- `HTTPProvider` (sync) or `AsyncHTTPProvider` (async) for HTTP transport
- `WebSocketProvider` (always async) for WebSocket transport

**Complete Examples:**
```python
# Local development (HTTP)
provider = ProviderBuilder().localhost().build()

# Local development (WebSocket)
provider = ProviderBuilder().localhost().ws().build()

# Mendoza testnet
provider = ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc").build()

# Async HTTP
provider = ProviderBuilder().localhost().async_mode().build()
```

---

## Account Management

### `NamedAccount`

Account wrapper with a human-readable name.

#### `NamedAccount.create(name)`
Create new account with random private key.

```python
account = NamedAccount.create("alice")
print(f"Address: {account.address}")
```

#### `NamedAccount.from_private_key(name, private_key)`
Create account from existing private key.

```python
account = NamedAccount.from_private_key("bob", "0x...")
```

#### `NamedAccount.from_wallet(name, wallet_json, password)`
Load account from encrypted wallet JSON.

```python
with open('wallet.json', 'r') as f:
    wallet_json = f.read()
account = NamedAccount.from_wallet("alice", wallet_json, "password")
```

---

## Type Reference

### Entity
```python
@dataclass(frozen=True)
class Entity:
    key: EntityKey | None
    fields: int  # Bitmask of populated fields

    # Metadata
    owner: ChecksumAddress | None
    created_at_block: int | None
    last_modified_at_block: int | None
    expires_at_block: int | None
    transaction_index: int | None
    operation_index: int | None

    # Content
    payload: bytes | None
    content_type: str | None

    # Attributes
    attributes: Attributes | None  # Dict[str, str | int]
```

### TransactionReceipt
```python
@dataclass(frozen=True)
class TransactionReceipt:
    tx_hash: TxHash
    block_number: int
    creates: list[CreateEvent]
    updates: list[UpdateEvent]
    extensions: list[ExtendEvent]
    owner_changes: list[ChangeOwnerEvent]
    deletes: list[DeleteEvent]
```

### Attributes
Type alias for `Dict[str, str | int]` - user-defined metadata.

**Rules:**
- Keys without `$` prefix (reserved for Arkiv)
- Values must be strings or non-negative integers

```python
attributes = Attributes({
    "type": "document",
    "version": 1,
    "status": "active",
    "userId": "alice123"
})
```

### EntityKey
Type alias for `int` - unique 256-bit identifier.

---

## Utilities

### `to_seconds(seconds=0, minutes=0, hours=0, days=0)`
Convert time duration to seconds.

```python
from arkiv import to_seconds

# Or use as method
expires_in = client.arkiv.to_seconds(hours=24)
expires_in = client.arkiv.to_seconds(days=7, hours=12)
expires_in = client.arkiv.to_seconds(minutes=30)
```

### `to_blocks(seconds=0, minutes=0, hours=0, days=0)`
Convert time duration to blocks (assumes 2 second block time).

```python
from arkiv import to_blocks

blocks = client.arkiv.to_blocks(hours=1)  # ~1800 blocks
```

---

## Constants

### Sorting
```python
from arkiv import STR, INT, ASC, DESC

# Used for ordering query results
order_by=[("created_at", DESC), ("version", ASC)]
```

### Field Masks
```python
from arkiv.types import (
    KEY, ATTRIBUTES, PAYLOAD, CONTENT_TYPE,
    EXPIRATION, OWNER, CREATED_AT, LAST_MODIFIED_AT,
    ALL, NONE
)

# Combine with | operator
fields = PAYLOAD | ATTRIBUTES | OWNER
```

---

## Error Handling

### Common Exceptions

**`ValueError`**
- Invalid parameters
- Entity not found
- No account configured

**`RuntimeError`**
- Transaction failed
- Contract operation failed

**`AttributeException`**
- Invalid attribute keys or values

**`EntityKeyException`**
- Invalid entity key format

**Example:**
```python
try:
    entity = client.arkiv.get_entity(entity_key)
except ValueError as e:
    print(f"Entity not found: {e}")
```

---

## Async API

All methods have async equivalents in `AsyncArkiv`:

```python
from arkiv import AsyncArkiv

async with AsyncArkiv(provider, account) as client:
    # Create entity
    entity_key, receipt = await client.arkiv.create_entity(
        payload=b"Hello",
        expires_in=3600
    )

    # Query entities
    async for entity in client.arkiv.query_entities('type = "log"'):
        print(entity.payload)

    # Get entity
    entity = await client.arkiv.get_entity(entity_key)
```

---

## Network Information

### Mendoza Testnet

**RPC URL:** `https://mendoza.hoodi.arkiv.network/rpc`

**WebSocket:** `wss://mendoza.hoodi.arkiv.network/rpc/ws`

**Explorer:** Coming soon

**Faucet:** Contact team on Discord

---

## Complete Example

```python
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder

# Setup
provider = ProviderBuilder().custom("https://mendoza.hoodi.arkiv.network/rpc").build()
account = NamedAccount.from_private_key("demo", "0x...")
client = Arkiv(provider=provider, account=account)

# Create entity
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Hello, Arkiv!",
    content_type="text/plain",
    attributes={"type": "greeting", "version": 1},
    expires_in=client.arkiv.to_seconds(hours=24)
)

# Read entity
entity = client.arkiv.get_entity(entity_key)
print(f"Payload: {entity.payload.decode('utf-8')}")

# Query entities
for entity in client.arkiv.query_entities(f'$owner = "{account.address}"'):
    print(f"Entity {entity.key}: {entity.attributes}")

# Update entity
receipt = client.arkiv.update_entity(
    entity_key=entity_key,
    payload=b"Updated!",
    expires_in=client.arkiv.to_seconds(hours=48)
)

# Delete entity
receipt = client.arkiv.delete_entity(entity_key)
```
