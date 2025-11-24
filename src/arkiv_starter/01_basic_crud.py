"""
Example 1: Basic CRUD Operations with Arkiv

This example demonstrates:
- Creating entities (storing data on-chain)
- Reading entities by entity key (their ID)
- Updating existing entities
- Deleting entities

Run this example: python examples/01_basic_crud.py
"""

from arkiv.provider import ProviderBuilder
from arkiv import Arkiv, NamedAccount
from arkiv.node import ArkivNode
from typing import cast
from web3.providers.base import BaseProvider


print("🚀 Step 1: Create local arkiv client (and node) ...")
client = Arkiv()
print(f"✅ Default client created with accounts: {client.accounts}")
print(f"✅ Default client account funding:  {client.eth.get_balance(client.eth.default_account)/10**18} ETH")

# Step 1: Start a local Arkiv node (runs in Docker)
print("\n🚀 Step 2: Constructing provider for custom RPC URL...")
local_node = client.node
assert local_node is not None, "Arkiv client should have started a node"
rpc_url = local_node.http_url
provider = cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build())
print(f"✅ Provider running: {provider}")

# Step 3a: Create and fund an account for transactions
print("\n🚀 Step 3: Creating named account...")
account = NamedAccount.create("demo-account")
local_node.fund_account(account)  # Fund with test tokens
print(f"✅ Created and funded account: {account.address}")
print(f"✅ Account funded with {client.eth.get_balance(account.address)/10**18} ETH")

print("\n🚀 Step 4: Creating custom client with specified provider and account...")
custom_client = Arkiv(provider, account=account)
print(f"Custom client: {custom_client}")

print("\n📝 Step 5: Creating entity...")
data = b"Hello, Arkiv! This is my first entity."
entity_key, receipt = custom_client.arkiv.create_entity(
    payload=data,
    expires_in=3600,  # Expires in 1 hour (3600 seconds)
    content_type="text/plain",
)
print(f"✅ Entity created! Receipt: {receipt}")
print(f"📦 Entity Key: {entity_key}")

print("\n📖 Step 6: Reading entity...")
entity = custom_client.arkiv.get_entity(entity_key)
print("✅ Retrieved entity:")
print(f"   Key: {entity.key}")
print(f"   Owner: {entity.owner}")
if entity.payload:
    print(f"   Content: {entity.payload.decode('utf-8')}")
print(f"   Content Type: {entity.content_type}")
print(f"   Expires At Block: {entity.expires_at_block}")

print("\n🔄 Step 7: Updating entity...")
new_data = b"Updated content - Arkiv makes data management easy!"
receipt = custom_client.arkiv.update_entity(
    entity_key=entity_key,
    payload=new_data,
    content_type="text/plain",
    expires_in=7200,  # Extend expiration to 2 hours
)
print(f"✅ Entity updated! Receipt: {receipt}")

# Verify the update
updated_entity = custom_client.arkiv.get_entity(entity_key)
if updated_entity.payload:
    print(f"📖 Updated content: {updated_entity.payload.decode('utf-8')}, expires at: {updated_entity.expires_at_block}")

print("\n🔄 Step 8: Extending entity...")
receipt = custom_client.arkiv.extend_entity(entity_key, extend_by=custom_client.arkiv.to_seconds(minutes=1))
print(f"✅ Entity extended! Receipt: {receipt}")

# Verify the extension
extended_entity = custom_client.arkiv.get_entity(entity_key)
print(f"Extended expires at: {extended_entity.expires_at_block}")

print("\n🔄 Step 9: Changing entity owner...")
next_owner = client.eth.default_account
receipt = custom_client.arkiv.change_owner(entity_key, new_owner=next_owner)
print(f"✅ Entity owner chanaged! Receipt: {receipt}")

# Verify the ownership transfer
transferred_entity = custom_client.arkiv.get_entity(entity_key)
print(f"New owner: {transferred_entity.owner}")

print("\n🗑️  Step 9: Deleting entity...")
receipt = client.arkiv.delete_entity(entity_key) # original owner is not allowed to delete
print(f"✅ Entity deleted! Receipt: {receipt}")

# Verify deletion
try:
    custom_client.arkiv.get_entity(entity_key)
    print("❌ Entity still exists (unexpected)")
except Exception:
    print("✅ Entity successfully deleted")

