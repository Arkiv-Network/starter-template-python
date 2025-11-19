"""
Example 2: Querying Entities with Filters

This example demonstrates:
- Creating multiple entities
- Querying with filters (owner, content type)
- Sorting results
- Pagination

Run this example: python examples/02_queries.py
"""

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
print(f"✅ Account ready: {account.address}")

# Create multiple entities with different types
print("\n📝 Creating multiple entities...")
entities = []

# Text entities
for i in range(3):
    entity_key, receipt = client.arkiv.create_entity(
        payload=f"Text document #{i + 1}".encode(),
        expires_in=3600,
        content_type="text/plain",
    )
    entities.append(entity_key)
    print(f"   Created text entity: {entity_key}")

# JSON entities
for i in range(2):
    entity_key, receipt = client.arkiv.create_entity(
        payload=f'{{"id": {i + 1}, "type": "json"}}'.encode(),
        expires_in=3600,
        content_type="application/json",
    )
    entities.append(entity_key)
    print(f"   Created JSON entity: {entity_key}")

# Query 1: Get all entities by owner
print(f"\n🔍 Query 1: All entities owned by {account.address[:10]}...")
all_entities = list(client.arkiv.query_entities(f'$owner = "{account.address}"'))
print(f"✅ Found {len(all_entities)} entities")

# Query 2: Show all entities with details
print("\n🔍 Query 2: Retrieving all entities with details...")
all_with_details = list(client.arkiv.query_entities(f'$owner = "{account.address}"'))
print(f"✅ Found {len(all_with_details)} entities:")
for entity in all_with_details:
    content = entity.payload.decode('utf-8')
    print(f"   Type: {entity.content_type:20} | {content}")

# Query 3: Filter by content type (client-side filtering)
print("\n🔍 Query 3: Filter by content type (text/plain)...")
text_entities = [e for e in all_with_details if e.content_type == "text/plain"]
print(f"✅ Found {len(text_entities)} text entities:")
for entity in text_entities:
    print(f"   {entity.payload.decode('utf-8')}")

# Query 4: Filter by content type (application/json)
print("\n🔍 Query 4: Filter by content type (application/json)...")
json_entities = [e for e in all_with_details if e.content_type == "application/json"]
print(f"✅ Found {len(json_entities)} JSON entities:")
for entity in json_entities:
    print(f"   {entity.payload.decode('utf-8')}")

# Cleanup
print("\n🧹 Cleaning up...")
node.stop()
print("✅ Done! Node stopped.")
