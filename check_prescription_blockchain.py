"""
Check prescription blockchain implementation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from patient_portal.prescription_models import Prescription
from blockchain.blockchain_service import get_blockchain_service

print("=" * 80)
print("PRESCRIPTION BLOCKCHAIN CHECK")
print("=" * 80)

# Get latest prescription
prescriptions = Prescription.objects.all().order_by('-created_at')
print(f"\n📋 Total prescriptions in database: {prescriptions.count()}")

if prescriptions.exists():
    latest = prescriptions.first()
    print(f"\n🔍 Latest Prescription Details:")
    print(f"   ID: {latest.id}")
    print(f"   Patient: {latest.patient.get_full_name()}")
    print(f"   Doctor: {latest.doctor.get_full_name()}")
    print(f"   Created: {latest.created_at}")
    print(f"   PDF Generated: {'✅ Yes' if latest.pdf_file else '❌ No'}")
    print(f"   PDF Hash: {latest.pdf_hash if latest.pdf_hash else '❌ Not generated'}")
    print(f"   QR Code: {'✅ Generated' if latest.qr_code else '❌ Not generated'}")
    print(f"   Blockchain TX: {latest.blockchain_tx_hash if latest.blockchain_tx_hash else '❌ Not stored'}")
    print(f"   Verified: {'✅ Yes' if latest.is_verified else '❌ No'}")
    
    # Check blockchain service
    print(f"\n🔗 Blockchain Service Status:")
    service = get_blockchain_service()
    print(f"   Connected: {'✅ Yes' if service.is_connected() else '❌ No'}")
    
    if service.is_connected():
        print(f"   Account: {service.account.address}")
        balance = service.get_balance()
        print(f"   Balance: {balance:.6f} ETH" if balance else "   Balance: ❌ Cannot fetch")
        print(f"   QR Logging Contract: {'✅ Loaded' if service.contract else '❌ Not loaded'}")
        print(f"   Prescription Contract: {'✅ Loaded' if service.prescription_contract else '❌ Not loaded'}")
        
        # Try to verify the hash on blockchain
        if latest.pdf_hash:
            print(f"\n🔍 Attempting to verify prescription hash on blockchain...")
            verification = service.verify_prescription_hash(latest.pdf_hash)
            
            if verification:
                if verification.get('exists'):
                    print(f"   ✅ PRESCRIPTION FOUND ON BLOCKCHAIN!")
                    print(f"   On-chain Prescription ID: {verification['prescription_id']}")
                    print(f"   Timestamp: {verification['timestamp']}")
                else:
                    print(f"   ❌ PRESCRIPTION NOT FOUND ON BLOCKCHAIN")
                    print(f"   This means the transaction was not sent or failed")
            else:
                print(f"   ⚠️  Verification failed (blockchain error)")
    
    # Show the actual hash for manual verification
    if latest.pdf_hash:
        print(f"\n📝 PDF Hash Details:")
        print(f"   Full Hash: {latest.pdf_hash}")
        print(f"   Hash Length: {len(latest.pdf_hash)} characters")
        print(f"   Hash Type: SHA-256")
    
    if latest.blockchain_tx_hash:
        print(f"\n🔗 Transaction Details:")
        print(f"   TX Hash: {latest.blockchain_tx_hash}")
        print(f"   Etherscan: https://sepolia.etherscan.io/tx/{latest.blockchain_tx_hash}")

else:
    print("\n❌ No prescriptions found in database")

print("\n" + "=" * 80)
