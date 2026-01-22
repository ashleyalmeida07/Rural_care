"""
Test script to verify blockchain integration works for new prescriptions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from patient_portal.prescription_models import Prescription
from patient_portal.consultation_models import Consultation
from django.contrib.auth import get_user_model
from blockchain.blockchain_service import store_prescription_hash, BlockchainService

User = get_user_model()

def test_new_prescription():
    print("="*80)
    print("TESTING BLOCKCHAIN INTEGRATION WITH NEW PRESCRIPTION")
    print("="*80)
    
    # Get or create test consultation
    try:
        consultation = Consultation.objects.first()
        if not consultation:
            print("❌ No consultations found. Please create a consultation first.")
            return
        
        print(f"\n📋 Using consultation: {consultation.id}")
        print(f"   Patient: {consultation.patient.first_name} {consultation.patient.last_name}")
        print(f"   Doctor: {consultation.doctor.first_name} {consultation.doctor.last_name}")
        
        # Create a test prescription
        from django.utils import timezone
        
        prescription = Prescription.objects.create(
            consultation=consultation,
            patient=consultation.patient,
            doctor=consultation.doctor,
            diagnosis="Test Diagnosis - Blockchain Integration Test",
            symptoms="Test symptoms for blockchain verification",
            doctor_notes="This is a test prescription to verify blockchain integration",
            follow_up_instructions="Follow-up after 7 days"
        )
        
        print(f"\n✅ Created test prescription: {prescription.id}")
        
        # Create a test hash
        test_hash = "a" * 64  # Dummy hash for testing
        
        print(f"\n🔗 Attempting to store on blockchain...")
        print(f"   Hash: {test_hash[:32]}...")
        print(f"   Patient ID: {prescription.patient.id}")
        print(f"   Doctor ID: {prescription.doctor.id}")
        
        # Store on blockchain
        result = store_prescription_hash(
            prescription_id=prescription.id,
            pdf_hash=test_hash,
            patient_id=prescription.patient.id,
            doctor_id=prescription.doctor.id
        )
        
        print(f"\n📊 Blockchain Storage Result:")
        if result and result.get('success'):
            print(f"   ✅ SUCCESS!")
            print(f"   TX Hash: {result['transaction_hash']}")
            print(f"   Block: {result.get('block_number', 'Pending')}")
            
            # Update prescription
            prescription.blockchain_tx_hash = result['transaction_hash']
            prescription.is_verified = True
            prescription.pdf_hash = test_hash
            prescription.save()
            
            print(f"\n✅ Prescription updated with blockchain data")
            
            # Verify on blockchain
            print(f"\n🔍 Verifying on blockchain...")
            bc_service = BlockchainService()
            verified = bc_service.verify_prescription_hash(test_hash)
            
            if verified:
                print(f"   ✅ VERIFIED on blockchain!")
                print(f"   Stored hash matches: {verified}")
            else:
                print(f"   ⚠️  Not found on blockchain (may take a few seconds)")
                
            # Show Etherscan link
            print(f"\n🌐 View on Etherscan:")
            print(f"   https://sepolia.etherscan.io/tx/{result['transaction_hash']}")
            
        else:
            print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
            
        print(f"\n🗑️  Cleaning up test prescription...")
        prescription.delete()
        print(f"   ✅ Test prescription deleted")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_new_prescription()
