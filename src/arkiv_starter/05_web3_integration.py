"""
Example 5: Web3.py Integration

This example demonstrates:
- Using Arkiv with existing web3.py code
- Accessing raw Web3 functionality
- Mixing Arkiv operations with standard Web3 calls
- Full CRUD lifecycle (create, read, update, delete)

Run this example: uv run python -m arkiv_starter.05_web3_integration
"""

from arkiv.provider import ProviderBuilder
from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode
from web3 import Web3
from typing import cast
from web3.providers.base import BaseProvider

# Setup: Start node and create client
print("🚀 Starting local Arkiv node...")
node = ArkivNode()
node.start()

# Create and fund account
provider = ProviderBuilder().node(node).build()
provider = cast(BaseProvider, provider) # cast for static type checkers

# Create and fund account
account = NamedAccount.create("web3-integration")
node.fund_account(account)

# Initialize client with account
client = Arkiv(provider, account=account)
print(f"✅ Account ready: {account.address}\n")

# ============================================================================
# Part 1: Standard Web3 Operations
# ============================================================================
print("🌐 Part 1: Standard Web3 Operations")
print("=" * 60)

# Get block information
latest_block = client.eth.get_block("latest")
print(f"📦 Latest Block Number: {latest_block['number']}")
print(f"   Timestamp: {latest_block['timestamp']}")
print(f"   Transaction Count: {len(latest_block['transactions'])}\n")

# Check account balance
balance_wei = client.eth.get_balance(account.address)
balance_eth = Web3.from_wei(balance_wei, "ether")
print("💰 Account Balance:")
print(f"   {balance_wei} wei")
print(f"   {balance_eth} ETH\n")

# Get chain ID
chain_id = client.eth.chain_id
print(f"🔗 Chain ID: {chain_id}\n")

# ============================================================================
# Part 2: Arkiv-Specific Operations
# ============================================================================
print("📦 Part 2: Arkiv-Specific Operations")
print("=" * 60)

# Create entity
print("📝 Creating entity with Arkiv...")
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Web3 integration example", 
    expires_in=3600, 
    content_type="text/plain"
)
print(f"   Transaction Hash: {receipt.tx_hash}")
print(f"   Block Number: {receipt.block_number}\n")

print(f"✅ Entity Created: Key {entity_key}\n")

# ============================================================================
# Part 3: Direct Contract Interaction (Advanced)
# ============================================================================
print("🔧 Part 3: Direct Contract Interaction")
print("=" * 60)

# Access the Arkiv contract directly
arkiv_contract = client.arkiv.contract
print(f"📜 Contract Address: {arkiv_contract.address}")

# Get entity using Arkiv's high-level API
entity = client.arkiv.get_entity(entity_key)
print(f"\n📖 Entity {entity_key} (via Arkiv SDK):")
print(f"   Owner: {entity.owner}")
print(f"   Content Type: {entity.content_type}")
print(f"   Expires At Block: {entity.expires_at_block}")
if entity.payload:
    print(f"   Content Length: {len(entity.payload)} bytes")
    print(f"   Content: {entity.payload.decode('utf-8')}\n")
else:
    print(f"   No payload content\n")

# ============================================================================
# Part 4: Updating and Deleting Entities
# ============================================================================
print("✍️  Part 4: Updating and Deleting Entities")
print("=" * 60)

# Update entity
print("🔄 Updating entity...")
update_receipt = client.arkiv.update_entity(
    entity_key,
    payload=b"Updated via Web3 example",
    expires_in=7200,
    content_type="text/plain"
)
print(f"   Transaction Hash: {update_receipt.tx_hash}")
print(f"   Block Number: {update_receipt.block_number}\n")

# Verify update
updated_entity = client.arkiv.get_entity(entity_key)
if updated_entity.payload:
    print(f"📖 Updated content: {updated_entity.payload.decode('utf-8')}\n")
else:
    print(f"📖 No payload content\n")

# Delete entity
print("🗑️  Deleting entity...")
delete_receipt = client.arkiv.delete_entity(entity_key)
print(f"   Transaction Hash: {delete_receipt.tx_hash}")
print(f"   Block Number: {delete_receipt.block_number}\n")

# Verify deletion (should return None or raise exception)
try:
    deleted_entity = client.arkiv.get_entity(entity_key)
    if deleted_entity:
        print(f"⚠️  Entity still exists")
    else:
        print(f"✅ Entity successfully deleted\n")
except Exception as e:
    print(f"✅ Entity successfully deleted (not found)\n")

# ============================================================================
# Summary
# ============================================================================
print("=" * 60)
print("📋 Summary:")
print("   ✅ Standard Web3 operations work seamlessly")
print("   ✅ Arkiv adds convenient entity management methods")
print("   ✅ Full CRUD operations on blockchain entities")
print("   ✅ Access to contract details and chain information")
print("=" * 60)

# Cleanup
print("\n🧹 Cleaning up...")
node.stop()
print("✅ Done! Node stopped.")
