"""
Insurance SIP Sample Data Population Script

This script populates the database with sample government schemes,
eligibility criteria, and insurance policies.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cancer_treatment_system.settings')
django.setup()

from Insurance_SIP.Insurance_SIP.models import GovernmentScheme, Eligibility, InsurancePolicy
import uuid

def populate_data():
    print("=" * 70)
    print("INSURANCE SIP - SAMPLE DATA POPULATION")
    print("=" * 70)
    
    # Clear existing data
    print("\n🗑️  Clearing existing data...")
    GovernmentScheme.objects.all().delete()
    InsurancePolicy.objects.all().delete()
    print("✅ Existing data cleared")
    
    # Create Government Schemes
    print("\n📋 Creating Government Schemes...")
    
    # 1. Ayushman Bharat
    scheme1_id = uuid.UUID('550e8400-e29b-41d4-a716-446655440001')
    scheme1 = GovernmentScheme.objects.create(
        id=scheme1_id,
        name="Ayushman Bharat (PM-JAY)",
        scheme_type="health",
        description="Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY) is a flagship scheme of Government of India which was launched as recommended by the National Health Policy 2017, to achieve the vision of Universal Health Coverage (UHC).",
        short_description="Free health insurance coverage up to ₹5 lakh per family per year for secondary and tertiary hospitalization.",
        coverage_amount=500000.00,
        benefits="""• Cashless treatment at empanelled hospitals
• Coverage for 1,393+ procedures
• Pre and post-hospitalization expenses
• No cap on family size
• Coverage across India""",
        required_documents="""• Ration Card
• SECC Data
• Aadhaar Card
• Address Proof
• Income Certificate""",
        application_steps="""1. Check eligibility on official website
2. Visit nearest Ayushman Mitra
3. Submit required documents
4. Get your Ayushman Card
5. Visit empanelled hospitals""",
        official_website="https://pmjay.gov.in/",
        is_active=True
    )
    print(f"✅ Created: {scheme1.name}")
    
    # 2. Pradhan Mantri Suraksha Bima Yojana
    scheme2_id = uuid.UUID('550e8400-e29b-41d4-a716-446655440002')
    scheme2 = GovernmentScheme.objects.create(
        id=scheme2_id,
        name="Pradhan Mantri Suraksha Bima Yojana",
        scheme_type="accident",
        description="PMSBY is a one year accident insurance scheme offering coverage for death or disability due to accident. The scheme is renewable on an annual basis.",
        short_description="Accident insurance cover of ₹2 lakh at just ₹12 per year premium.",
        coverage_amount=200000.00,
        benefits="""• Death benefit: ₹2 lakh
• Total permanent disability: ₹2 lakh
• Partial permanent disability: ₹1 lakh
• Annual premium: Only ₹12
• Auto-debit facility""",
        required_documents="""• Bank Account
• Aadhaar Card
• Age Proof (18-70 years)
• Consent Form""",
        application_steps="""1. Visit your bank branch
2. Fill enrolment form
3. Give auto-debit consent
4. Premium will be deducted annually
5. Get SMS confirmation""",
        official_website="https://www.india.gov.in/spotlight/pradhan-mantri-suraksha-bima-yojana",
        is_active=True
    )
    print(f"✅ Created: {scheme2.name}")
    
    # 3. Atal Pension Yojana
    scheme3_id = uuid.UUID('550e8400-e29b-41d4-a716-446655440003')
    scheme3 = GovernmentScheme.objects.create(
        id=scheme3_id,
        name="Atal Pension Yojana",
        scheme_type="pension",
        description="APY is a pension scheme for all citizens of India, particularly the poor, the underprivileged and the workers in the unorganised sector.",
        short_description="Guaranteed monthly pension starting from ₹1,000 to ₹5,000 after age 60.",
        coverage_amount=60000.00,
        benefits="""• Guaranteed pension amount
• Government co-contribution
• Nomination facility
• Minimum pension: ₹1,000/month
• Maximum pension: ₹5,000/month""",
        required_documents="""• Aadhaar Card
• Bank Account
• Mobile Number
• Age Proof (18-40 years)""",
        application_steps="""1. Visit your bank
2. Fill APY registration form
3. Choose pension amount
4. Start monthly contributions
5. Get pension at age 60""",
        official_website="https://npscra.nsdl.co.in/atal-pension-yojana.php",
        is_active=True
    )
    print(f"✅ Created: {scheme3.name}")
    
    # Create Eligibility Criteria
    print("\n🎯 Creating Eligibility Criteria...")
    
    Eligibility.objects.create(
        id=uuid.UUID('650e8400-e29b-41d4-a716-446655440001'),
        scheme=scheme1,
        min_age=0,
        max_age=100,
        max_income=500000,
        additional_criteria="Must be from economically weaker sections as per SECC 2011 data"
    )
    print(f"✅ Created eligibility for: {scheme1.name}")
    
    Eligibility.objects.create(
        id=uuid.UUID('650e8400-e29b-41d4-a716-446655440002'),
        scheme=scheme2,
        min_age=18,
        max_age=70,
        additional_criteria="Must have savings bank account. Enrolled through auto-debit facility."
    )
    print(f"✅ Created eligibility for: {scheme2.name}")
    
    Eligibility.objects.create(
        id=uuid.UUID('650e8400-e29b-41d4-a716-446655440003'),
        scheme=scheme3,
        min_age=18,
        max_age=40,
        additional_criteria="Must have savings bank account. Not covered under any statutory social security scheme."
    )
    print(f"✅ Created eligibility for: {scheme3.name}")
    
    # Create Insurance Policies
    print("\n💼 Creating Insurance Policies...")
    
    # 1. HealthFirst Plus
    policy1 = InsurancePolicy.objects.create(
        id=uuid.UUID('750e8400-e29b-41d4-a716-446655440001'),
        name="HealthFirst Plus",
        policy_type="health",
        description="Comprehensive health insurance plan covering hospitalization, pre and post hospitalization expenses, daycare procedures, and ambulance charges.",
        short_description="Complete health protection with coverage up to ₹10 lakh and cashless treatment at 10,000+ hospitals.",
        premium_per_month=599.00,
        coverage_amount=1000000.00,
        key_features="""• Cashless treatment at 10,000+ network hospitals
• Coverage for 30 days pre-hospitalization
• 60 days post-hospitalization coverage
• Daycare procedures covered
• Free health checkup every year
• No room rent capping""",
        cashless_hospitals=True,
        claim_support=True,
        add_ons_available="""• Critical illness cover
• Personal accident cover
• Maternity cover
• Mental health cover""",
        min_age=18,
        max_age=65,
        is_active=True
    )
    print(f"✅ Created: {policy1.name}")
    
    # 2. LifeSecure Family Plan
    policy2 = InsurancePolicy.objects.create(
        id=uuid.UUID('750e8400-e29b-41d4-a716-446655440002'),
        name="LifeSecure Family Plan",
        policy_type="family",
        description="Affordable family health insurance covering parents, spouse, and children with lifetime renewability.",
        short_description="Cover entire family with single premium starting at ₹899/month.",
        premium_per_month=899.00,
        coverage_amount=1500000.00,
        key_features="""• Family floater coverage
• Covers parents, spouse, children
• Cashless hospitals across India
• Maternity coverage included
• New born baby covered from day 1
• Unlimited automatic restoration""",
        cashless_hospitals=True,
        claim_support=True,
        add_ons_available="""• International coverage
• Home healthcare
• Second medical opinion
• Organ donor expenses""",
        min_age=21,
        max_age=75,
        is_active=True
    )
    print(f"✅ Created: {policy2.name}")
    
    # 3. Senior Care Shield
    policy3 = InsurancePolicy.objects.create(
        id=uuid.UUID('750e8400-e29b-41d4-a716-446655440003'),
        name="Senior Care Shield",
        policy_type="senior",
        description="Specially designed health insurance for senior citizens with pre-existing disease coverage.",
        short_description="Senior citizen plan with coverage up to ₹5 lakh, covering pre-existing diseases.",
        premium_per_month=1299.00,
        coverage_amount=500000.00,
        key_features="""• Pre-existing diseases covered
• No medical tests up to age 70
• Coverage for age-related illnesses
• Domiciliary hospitalization
• AYUSH treatment covered
• Free annual health checkup""",
        cashless_hospitals=True,
        claim_support=True,
        add_ons_available="""• Alzheimers cover
• Long term care benefit
• Mobility aids
• Home nursing""",
        min_age=60,
        max_age=80,
        is_active=True
    )
    print(f"✅ Created: {policy3.name}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ SAMPLE DATA POPULATION COMPLETED!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   • Government Schemes: {GovernmentScheme.objects.count()}")
    print(f"   • Eligibility Criteria: {Eligibility.objects.count()}")
    print(f"   • Insurance Policies: {InsurancePolicy.objects.count()}")
    print(f"\n🌐 Access the application at: http://localhost:8000/insurance/")
    print(f"🔧 Admin panel at: http://localhost:8000/admin/")
    print("=" * 70)

if __name__ == "__main__":
    try:
        populate_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
