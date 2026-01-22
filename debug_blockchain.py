"""
Test blockchain service initialization
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from blockchain.blockchain_service import BlockchainService
from django.conf import settings
from pathlib import Path

print("=" * 80)
print("BLOCKCHAIN SERVICE DEBUG")
print("=" * 80)

print("\n📋 Settings Check:")
print(f"   PRESCRIPTION_CONTRACT_ADDRESS: {getattr(settings, 'PRESCRIPTION_CONTRACT_ADDRESS', 'NOT SET')}")
print(f"   BLOCKCHAIN_CONTRACT_ADDRESS: {getattr(settings, 'BLOCKCHAIN_CONTRACT_ADDRESS', 'NOT SET')}")
print(f"   ALCHEMY_RPC_URL: {getattr(settings, 'ALCHEMY_RPC_URL', 'NOT SET')[:50]}...")
print(f"   BLOCKCHAIN_ENABLED: {getattr(settings, 'BLOCKCHAIN_ENABLED', 'NOT SET')}")

print("\n📁 File Check:")
abi_path = Path('blockchain/contract_abi.json')
print(f"   contract_abi.json exists: {abi_path.exists()}")
if abi_path.exists():
    print(f"   File size: {abi_path.stat().st_size} bytes")

print("\n🔧 Creating BlockchainService instance...")
service = BlockchainService()

print(f"\n🔗 Service Status:")
print(f"   connected: {service.connected}")
print(f"   w3: {service.w3 is not None}")
print(f"   account: {service.account.address if service.account else 'None'}")
print(f"   contract (QR logging): {service.contract is not None}")
print(f"   prescription_contract: {service.prescription_contract is not None}")

if service.prescription_contract:
    print(f"\n✅ Prescription Contract Loaded Successfully!")
    print(f"   Address: {service.prescription_contract.address}")
    
    # Try to call a read function
    try:
        stats = service.prescription_contract.functions.getStats().call()
        print(f"   Total Prescriptions on Chain: {stats[0]}")
        print(f"   Contract Owner: {stats[1]}")
    except Exception as e:
        print(f"   Error calling contract: {e}")
else:
    print(f"\n❌ Prescription Contract NOT Loaded")

print("\n" + "=" * 80)
