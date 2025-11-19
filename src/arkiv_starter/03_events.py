"""
Example 3: Listening to Blockchain Events

This example demonstrates:
- Subscribing to entity lifecycle events
- Real-time event monitoring
- Processing event data

Run this example: python examples/03_events.py
"""

import time

from arkiv.provider import ProviderBuilder
from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode

# Setup: Start node and create client
print("🚀 Starting local Arkiv node...")
node = ArkivNode()
node.start()

provider = ProviderBuilder().node(node).build()

# Create and fund an account
account = NamedAccount.create("demo-account")
node.fund_account(account)

client = Arkiv(provider, account=account)
print(f"✅ Account ready: {account.address}\n")

# Get the Arkiv contract for event listening
arkiv_contract = client.arkiv.contract

# Listen for Arkiv entity events
print("👂 Setting up event listeners...")
print("   - ArkivEntityCreated")
print("   - ArkivEntityUpdated")
print("   - ArkivEntityDeleted\n")

# Create event filters
created_filter = arkiv_contract.events.ArkivEntityCreated.create_filter(from_block="latest")
updated_filter = arkiv_contract.events.ArkivEntityUpdated.create_filter(from_block="latest")
deleted_filter = arkiv_contract.events.ArkivEntityDeleted.create_filter(from_block="latest")

print("📝 Performing operations to trigger events...\n")

# Operation 1: Create entity
print("1️⃣  Creating entity...")
entity_key, receipt = client.arkiv.create_entity(
    payload=b"Event monitoring test", expires_in=3600, content_type="text/plain"
)
print(f"   ✅ Entity {entity_key} created\n")

time.sleep(1)  # Give events time to propagate

# Check for ArkivEntityCreated events
created_events = created_filter.get_new_entries()
for event in created_events:
    print("🎉 ArkivEntityCreated Event Received!")
    print(f"   Entity Key: {hex(event['args']['entityKey'])}")
    print(f"   Owner: {event['args']['ownerAddress']}")
    print(f"   Expiration Block: {event['args']['expirationBlock']}")
    print(f"   Block Number: {event['blockNumber']}\n")

# Operation 2: Update entity
print("2️⃣  Updating entity...")
receipt = client.arkiv.update_entity(
    entity_key=entity_key,
    payload=b"Updated content for event test",
    expires_in=7200,
    content_type="text/plain",
)
print(f"   ✅ Entity {entity_key} updated\n")

time.sleep(1)

# Check for ArkivEntityUpdated events
updated_events = updated_filter.get_new_entries()
for event in updated_events:
    print("🔄 ArkivEntityUpdated Event Received!")
    print(f"   Entity Key: {hex(event['args']['entityKey'])}")
    print(f"   Owner: {event['args']['ownerAddress']}")
    print(f"   Block Number: {event['blockNumber']}\n")

# Operation 3: Delete entity
print("3️⃣  Deleting entity...")
receipt = client.arkiv.delete_entity(entity_key)
print(f"   ✅ Entity {entity_key} deleted\n")

time.sleep(1)

# Check for ArkivEntityDeleted events
deleted_events = deleted_filter.get_new_entries()
for event in deleted_events:
    print("🗑️  ArkivEntityDeleted Event Received!")
    print(f"   Entity Key: {hex(event['args']['entityKey'])}")
    print(f"   Owner: {event['args']['ownerAddress']}")
    print(f"   Block Number: {event['blockNumber']}\n")

# Demonstrate historical event queries
print("📜 Querying historical events...")
from_block = receipt.block_number
to_block = "latest"

all_created_events = arkiv_contract.events.ArkivEntityCreated.get_logs(
    from_block=from_block, to_block=to_block, argument_filters={"ownerAddress": account.address}
)
print(f"✅ Found {len(all_created_events)} ArkivEntityCreated events for this account")

# Cleanup
print("\n🧹 Cleaning up...")
node.stop()
print("✅ Done! Node stopped.")
