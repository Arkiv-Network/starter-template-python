"""
Example 4: Web3.py Integration

This example demonstrates:
- Using Arkiv with existing web3.py code
- Accessing raw Web3 functionality
- Mixing Arkiv operations with standard Web3 calls

Run this example: python examples/04_web3_integration.py
"""

from arkiv.provider import ProviderBuilder
from eth_account import Account
from web3 import Web3

from arkiv import Arkiv
from arkiv.node import ArkivNode

# Setup: Start node and create client
print("🚀 Starting local Arkiv node...")
node = ArkivNode()
node.start()

provider = ProviderBuilder().node(node).build()
client = Arkiv(provider)

# Create and fund account
account = Account.create()
node.fund_account(account)
client.eth.default_account = account
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
tx_hash = client.arkiv.create_entity(
    payload=b"Web3 integration example", expires_in=3600, content_type="text/plain"
)
print(f"   Transaction Hash: {tx_hash.hex()}")

# Wait and get receipt (standard Web3 call)
receipt = client.eth.wait_for_transaction_receipt(tx_hash)
print(f"   Block Number: {receipt['blockNumber']}")
print(f"   Gas Used: {receipt['gasUsed']}\n")

# Extract entity ID from logs
entity_id = int(receipt["logs"][0]["topics"][1].hex(), 16)
print(f"✅ Entity Created: ID {entity_id}\n")

# ============================================================================
# Part 3: Direct Contract Interaction (Advanced)
# ============================================================================
print("🔧 Part 3: Direct Contract Interaction")
print("=" * 60)

# Access the Arkiv contract directly
arkiv_contract = client.arkiv.contract
print(f"📜 Contract Address: {arkiv_contract.address}")

# Call contract methods directly
entity_count = arkiv_contract.functions.getEntityCount().call()
print(f"📊 Total Entity Count: {entity_count}")

# Get entity using direct contract call
entity_data = arkiv_contract.functions.getEntity(entity_id).call()
print(f"\n📖 Entity {entity_id} (via direct contract call):")
print(f"   Owner: {entity_data[0]}")
print(f"   Content Type: {entity_data[1]}")
print(f"   Expires At: {entity_data[2]}")
print(f"   Content Length: {len(entity_data[3])} bytes")
print(f"   Content: {entity_data[3].decode('utf-8')}\n")

# ============================================================================
# Part 4: Transaction Signing (Manual)
# ============================================================================
print("✍️  Part 4: Manual Transaction Signing")
print("=" * 60)

# Build transaction manually
print("🔨 Building transaction manually...")
nonce = client.eth.get_transaction_count(account.address)

# Prepare update transaction
update_txn = arkiv_contract.functions.updateEntity(
    entity_id,
    b"Manually signed update",
    int(client.eth.get_block("latest")["number"]) + 1800,  # expires_at in blocks
    "text/plain",
).build_transaction(
    {
        "from": account.address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": client.eth.gas_price,
    }
)

# Sign transaction
print("✍️  Signing transaction...")
signed_txn = client.eth.account.sign_transaction(update_txn, account.key)

# Send signed transaction
print("📤 Sending signed transaction...")
tx_hash = client.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"   Transaction Hash: {tx_hash.hex()}")

# Wait for confirmation
receipt = client.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ Transaction mined in block {receipt['blockNumber']}\n")

# Verify update
updated_entity = client.arkiv.get_entity(entity_id)
print(f"📖 Updated content: {updated_entity.content.decode('utf-8')}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 60)
print("📋 Summary:")
print("   ✅ Standard Web3 operations work seamlessly")
print("   ✅ Arkiv adds convenient entity management methods")
print("   ✅ Direct contract access available when needed")
print("   ✅ Full control over transaction signing")
print("=" * 60)

# Cleanup
print("\n🧹 Cleaning up...")
node.stop()
print("✅ Done! Node stopped.")
