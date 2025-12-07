"""
Example 5: Querying Entities with Filters

This example demonstrates:
- Creating multiple entities
- Querying with the fluent query builder
- Filtering with typed attributes
- Sorting results

Run this example: uv run python -m arkiv_starter.05_queries
"""

from arkiv import Arkiv, IntAttr, IntSort, StrAttr
from arkiv.types import DESC, Attributes

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
        attributes=Attributes({"idx": entity_idx}),
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
        attributes=Attributes({"idx": entity_idx}),
        expires_in=client.arkiv.to_seconds(hours=1),
    )
    entity_idx += 1
    entities.append(entity_key)
    print(f"   Created JSON entity: {entity_key}")

# Query 1: Retrieve all entities with details
# Define typed attributes
owner = StrAttr("$owner")
idx = IntAttr("idx")

print(f"\n🔍 Query 1: Retrieving all entities with details...")
all_with_details = list(client.arkiv.select().where(owner == account).fetch())
print(f"✅ Found {len(all_with_details)} entities:")
for entity in all_with_details:
    if entity.payload:
        content = entity.payload.decode('utf-8')
        print(f"   Type: {entity.content_type:20} | {content:30} | {entity.attributes}")

# Query 2: Retrieve entities filtered by idx and sorted by idx descending
idx_desc = IntSort("idx", DESC)

print("\n🔍 Query 2: Retrieving filtered (idx > 1 and idx < 5) and sorted (idx desc) entities")
filtered_and_sorted = list(client.arkiv.select().where((idx > 1) & (idx < 5)).order_by(idx_desc).fetch())
print(f"✅ Found {len(filtered_and_sorted)} entities:")
for entity in filtered_and_sorted:
    if entity.payload:
        content = entity.payload.decode('utf-8')
        print(f"   Type: {entity.content_type:20} | {content:30} | {entity.attributes}")

# Cleanup
client.node.stop()
print("\n✅ Node stopped.")
