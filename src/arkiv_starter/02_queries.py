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
from arkiv.types import OrderByAttribute, QueryOptions, INT, DESC

# Setup: Start node and create client
print("🚀 Starting local Arkiv node and client ...")
client = Arkiv()
account = client.eth.default_account
print(f"✅ Client ready with account: {account}")

# Create multiple entities with different types
print("\n📝 Creating multiple entities...")
entities = []
entity_idx = 1

# Text entities
for i in range(3):
    entity_key, receipt = client.arkiv.create_entity(
        payload=f"Text document #{i + 1}".encode(),
        content_type="text/plain",
        attributes={"idx": entity_idx},
        expires_in=client.arkiv.to_seconds(hours=1),
    )
    entity_idx += 1
    entities.append(entity_key)
    print(f"   Created text entity: {entity_key}")

# JSON entities
for i in range(2):
    entity_key, receipt = client.arkiv.create_entity(
        payload=f'{{"id": {i + 1}, "type": "json"}}'.encode(),
        content_type="application/json",
        attributes={"idx": entity_idx},
        expires_in=client.arkiv.to_seconds(hours=1),
    )
    entity_idx += 1
    entities.append(entity_key)
    print(f"   Created JSON entity: {entity_key}")

print(f"\n🔍 Query 1: All entities owned by {account[:10]}...")
all_entities = list(client.arkiv.query_entities(f'$owner = "{account}"'))
print(f"✅ Found {len(all_entities)} entities")

print("\n🔍 Query 2: Retrieving all entities with details...")
all_with_details = list(client.arkiv.query_entities(f'$owner = "{account}"'))
print(f"✅ Found {len(all_with_details)} entities:")
for entity in all_with_details:
    content = entity.payload.decode('utf-8')
    print(f"   Type: {entity.content_type:20} | {content:30} | {entity.attributes}")

print("\n🔍 Query 3: Retrieving filtered (idx > 1 and idx < 5) and sorted (idx desc) entities")
sort = OrderByAttribute("idx", INT, DESC)
options = QueryOptions(order_by=[sort])
filtered_and_sorted = list(client.arkiv.query_entities(f"idx > 1 and idx < 5", options=options))
print(f"✅ Found {len(filtered_and_sorted)} entities:")
for entity in filtered_and_sorted:
    content = entity.payload.decode('utf-8')
    print(f"   Type: {entity.content_type:20} | {content:30} | {entity.attributes}")

print("\n🔍 Query 4: Filter by content type (application/json)...")
json_entities = [e for e in all_with_details if e.content_type == "application/json"]
print(f"✅ Found {len(json_entities)} JSON entities:")
for entity in json_entities:
    print(f"   {entity.payload.decode('utf-8')}")

