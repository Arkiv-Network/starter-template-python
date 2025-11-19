"""
Example 1: Basic CRUD Operations with Arkiv

This example demonstrates:
- Creating entities (storing data on-chain)
- Reading entities by ID
- Updating existing entities
- Deleting entities

Run this example: python examples/01_basic_crud.py
"""

from arkiv.provider import ProviderBuilder
from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode

# Step 1: Start a local Arkiv node (runs in Docker)
print("🚀 Starting local Arkiv node...")
node = ArkivNode()
node.start()
print(f"✅ Node running at {node.http_url}")

# Step 2: Create a provider and client
provider = ProviderBuilder().node(node).build()

# Step 3: Create and fund an account for transactions
account = NamedAccount.create("demo-account")
print(f"\n💰 Created account: {account.address}")
node.fund_account(account)  # Fund with test tokens

client = Arkiv(provider, account=account)
print(f"✅ Account funded with {client.eth.get_balance(account.address)} wei")

# Step 4: CREATE - Store data on-chain
print("\n📝 Creating entity...")
data = b"Hello, Arkiv! This is my first entity."
entity_key, receipt = client.arkiv.create_entity(
    payload=data,
    expires_in=3600,  # Expires in 1 hour (3600 seconds)
    content_type="text/plain",
)
print(f"✅ Entity created! Transaction: {receipt.tx_hash}")
print(f"📦 Entity Key: {entity_key}")

# Step 5: READ - Retrieve the entity
print("\n📖 Reading entity...")
entity = client.arkiv.get_entity(entity_key)
print("✅ Retrieved entity:")
print(f"   Key: {entity.key}")
print(f"   Owner: {entity.owner}")
print(f"   Content: {entity.payload.decode('utf-8')}")
print(f"   Content Type: {entity.content_type}")
print(f"   Expires At Block: {entity.expires_at_block}")

# Step 6: UPDATE - Modify the entity
print("\n🔄 Updating entity...")
new_data = b"Updated content - Arkiv makes data management easy!"
receipt = client.arkiv.update_entity(
    entity_key=entity_key,
    payload=new_data,
    expires_in=7200,  # Extend expiration to 2 hours
    content_type="text/plain",
)
print(f"✅ Entity updated! Transaction: {receipt.tx_hash}")

# Verify the update
updated_entity = client.arkiv.get_entity(entity_key)
print(f"📖 Updated content: {updated_entity.payload.decode('utf-8')}")

# Step 7: DELETE - Remove the entity
print("\n🗑️  Deleting entity...")
receipt = client.arkiv.delete_entity(entity_key)
print(f"✅ Entity deleted! Transaction: {receipt.tx_hash}")

# Verify deletion
try:
    client.arkiv.get_entity(entity_key)
    print("❌ Entity still exists (unexpected)")
except Exception:
    print("✅ Entity successfully deleted")

# Cleanup
print("\n🧹 Cleaning up...")
node.stop()
print("✅ Done! Node stopped.")
