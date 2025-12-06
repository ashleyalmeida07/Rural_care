from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .supabase_client import get_supabase_client
from .models import User, PatientProfile, DoctorProfile, DoctorKYC
import json
from datetime import datetime

def home(request):
    """Home page"""
    if request.user.is_authenticated:
        if request.user.user_type == 'patient':
            return redirect('patient_dashboard')
        elif request.user.user_type == 'doctor':
            return redirect('doctor_dashboard')
    return render(request, 'authentication/home.html')

def login_page(request):
    """Login selection page"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'authentication/login.html')

def patient_login(request):
    """Patient login page"""
    if request.user.is_authenticated:
        # If user is already logged in as a patient, go to patient dashboard
        if request.user.user_type == 'patient':
            messages.info(request, 'You are already logged in as a patient.')
            return redirect('patient_dashboard')
        # If user is logged in as a doctor, redirect to doctor dashboard
        elif request.user.user_type == 'doctor':
            messages.warning(request, 'You are logged in as a doctor. Please logout first to access patient login.')
            return redirect('doctor_dashboard')
    return render(request, 'authentication/patient_login.html')

def doctor_login(request):
    """Doctor login page"""
    if request.user.is_authenticated:
        # If user is already logged in as a doctor, go to doctor dashboard
        if request.user.user_type == 'doctor':
            messages.info(request, 'You are already logged in as a doctor.')
            return redirect('doctor_dashboard')
        # If user is logged in as a patient, redirect to patient dashboard
        elif request.user.user_type == 'patient':
            messages.warning(request, 'You are logged in as a patient. Please logout first to access doctor login.')
            return redirect('patient_dashboard')
    return render(request, 'authentication/doctor_login.html')

@csrf_exempt
def auth_callback(request):
    """Handle Supabase authentication callback - supports both GET and POST"""
    
    # Handle GET request (OAuth redirect from Supabase)
    if request.method == 'GET':
        # Store the user_type from query params if available
        user_type = request.GET.get('user_type', 'patient')
        
        # Render a page that will handle the hash fragment
        return render(request, 'authentication/auth_callback.html', {
            'user_type': user_type
        })
    
    # Handle POST request (from JavaScript after extracting tokens)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            access_token = data.get('access_token')
            user_type = data.get('user_type', 'patient')
            
            if not access_token:
                return JsonResponse({'error': 'Missing access token'}, status=400)
            
            # Get user info from Supabase
            supabase = get_supabase_client()
            
            try:
                # Set the session with the access token
                supabase.auth.set_session(access_token, data.get('refresh_token', ''))
                user_response = supabase.auth.get_user(access_token)
            except Exception as e:
                return JsonResponse({'error': f'Supabase error: {str(e)}'}, status=401)
            
            if not user_response or not user_response.user:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            
            supabase_user = user_response.user
            
            # Get or create Django user
            user, created = User.objects.get_or_create(
                supabase_user_id=supabase_user.id,
                defaults={
                    'username': supabase_user.email.split('@')[0] + '_' + user_type,
                    'email': supabase_user.email,
                    'user_type': user_type,
                    'first_name': supabase_user.user_metadata.get('full_name', '').split()[0] if supabase_user.user_metadata.get('full_name') else '',
                    'last_name': ' '.join(supabase_user.user_metadata.get('full_name', '').split()[1:]) if supabase_user.user_metadata.get('full_name') else '',
                    'profile_picture': supabase_user.user_metadata.get('avatar_url', ''),
                }
            )
            
            # If user already exists with a different role, prevent login
            if not created and user.user_type != user_type:
                return JsonResponse({
                    'error': f'This account is registered as a {user.user_type}. Please use the {user.user_type} login.',
                    'redirect_url': f'/login/{user.user_type}/' if user.user_type in ['patient', 'doctor'] else '/login/'
                }, status=403)
            
            # Create profile based on user type if user was just created
            if created:
                if user_type == 'patient':
                    PatientProfile.objects.create(user=user)
                elif user_type == 'doctor':
                    DoctorProfile.objects.create(
                        user=user,
                        license_number=f"TEMP_{user.id}"  # Should be updated later
                    )
            
            # Store tokens in session
            request.session['access_token'] = access_token
            request.session['refresh_token'] = data.get('refresh_token', '')
            request.session['user_type'] = user_type
            
            # Login user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Determine redirect URL
            if user_type == 'patient':
                redirect_url = '/patient/dashboard/'
            else:
                redirect_url = '/doctor/dashboard/'
            
            return JsonResponse({
                'success': True,
                'redirect_url': redirect_url
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def logout_view(request):
    """Logout user"""
    try:
        # Sign out from Supabase
        access_token = request.session.get('access_token')
        if access_token:
            supabase = get_supabase_client()
            supabase.auth.sign_out()
    except:
        pass
    
    # Clear session
    request.session.flush()
    
    # Logout from Django
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def patient_dashboard(request):
    """Patient dashboard"""
    if not request.user.is_authenticated or request.user.user_type != 'patient':
        return redirect('patient_login')
    return render(request, 'authentication/patient_dashboard.html')

def doctor_dashboard(request):
    """Doctor dashboard"""
    if not request.user.is_authenticated or request.user.user_type != 'doctor':
        return redirect('doctor_login')
    
    doctor_profile = DoctorProfile.objects.get(user=request.user)
    
    try:
        kyc = DoctorKYC.objects.get(doctor=doctor_profile)
    except DoctorKYC.DoesNotExist:
        kyc = None
    
    context = {
        'kyc': kyc,
        'doctor_profile': doctor_profile
    }
    
    return render(request, 'authentication/doctor_dashboard.html', context)


def kyc_status(request):
    """Display KYC status for doctor"""
    if not request.user.is_authenticated or request.user.user_type != 'doctor':
        return redirect('doctor_login')
    
    doctor_profile = DoctorProfile.objects.get(user=request.user)
    
    try:
        kyc = DoctorKYC.objects.get(doctor=doctor_profile)
    except DoctorKYC.DoesNotExist:
        kyc = None
    
    context = {
        'kyc': kyc,
        'doctor_profile': doctor_profile
    }
    
    return render(request, 'authentication/kyc_status.html', context)


def kyc_form(request):
    """KYC form for doctors"""
    if not request.user.is_authenticated or request.user.user_type != 'doctor':
        return redirect('doctor_login')
    
    doctor_profile = DoctorProfile.objects.get(user=request.user)
    
    try:
        kyc = DoctorKYC.objects.get(doctor=doctor_profile)
        # If already approved, redirect
        if kyc.status == 'approved':
            messages.info(request, 'Your KYC is already approved.')
            return redirect('doctor_dashboard')
    except DoctorKYC.DoesNotExist:
        kyc = None
    
    if request.method == 'POST':
        # Create or update KYC
        kyc_data = {
            'full_name': request.POST.get('full_name'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'gender': request.POST.get('gender'),
            'nationality': request.POST.get('nationality'),
            'personal_email': request.POST.get('personal_email'),
            'mobile_number': request.POST.get('mobile_number'),
            'residential_address': request.POST.get('residential_address'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'postal_code': request.POST.get('postal_code'),
            'country': request.POST.get('country'),
            'license_number_verified': request.POST.get('license_number_verified'),
            'license_issuing_authority': request.POST.get('license_issuing_authority'),
            'license_issue_date': request.POST.get('license_issue_date'),
            'license_expiry_date': request.POST.get('license_expiry_date'),
            'medical_degree': request.POST.get('medical_degree'),
            'medical_university': request.POST.get('medical_university'),
            'graduation_year': request.POST.get('graduation_year'),
            'current_hospital': request.POST.get('current_hospital'),
            'designation': request.POST.get('designation'),
            'department_specialty': request.POST.get('department_specialty'),
            'years_of_practice': request.POST.get('years_of_practice'),
            'identity_document_type': request.POST.get('identity_document_type'),
            'identity_document_number': request.POST.get('identity_document_number'),
            'address_proof_type': request.POST.get('address_proof_type'),
            'status': 'pending',
            'submitted_at': datetime.now(),
        }
        
        # Handle file uploads
        if 'license_document' in request.FILES:
            kyc_data['license_document'] = request.FILES['license_document']
        if 'degree_certificate' in request.FILES:
            kyc_data['degree_certificate'] = request.FILES['degree_certificate']
        if 'employment_document' in request.FILES:
            kyc_data['employment_document'] = request.FILES['employment_document']
        if 'identity_document_file' in request.FILES:
            kyc_data['identity_document_file'] = request.FILES['identity_document_file']
        if 'address_proof_file' in request.FILES:
            kyc_data['address_proof_file'] = request.FILES['address_proof_file']
        
        if kyc:
            # Update existing KYC
            for key, value in kyc_data.items():
                if value is not None:
                    setattr(kyc, key, value)
            kyc.save()
        else:
            # Create new KYC
            kyc_data['doctor'] = doctor_profile
            kyc = DoctorKYC.objects.create(**kyc_data)
        
        messages.success(request, 'KYC information submitted successfully. Your application is under review.')
        return redirect('kyc_status')
    
    context = {
        'kyc': kyc,
        'doctor_profile': doctor_profile,
        'gender_choices': [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        'identity_doc_types': [('passport', 'Passport'), ('aadhaar', 'Aadhaar'), ('national_id', 'National ID'), ('driving_license', 'Driving License')],
        'address_proof_types': [('utility_bill', 'Utility Bill'), ('rental_agreement', 'Rental Agreement'), ('property_deed', 'Property Deed'), ('bank_statement', 'Bank Statement')],
    }
    
    return render(request, 'authentication/kyc_form.html', context)


def kyc_preview(request):
    """Preview submitted KYC"""
    if not request.user.is_authenticated or request.user.user_type != 'doctor':
        return redirect('doctor_login')
    
    doctor_profile = DoctorProfile.objects.get(user=request.user)
    
    try:
        kyc = DoctorKYC.objects.get(doctor=doctor_profile)
    except DoctorKYC.DoesNotExist:
        messages.error(request, 'No KYC found. Please complete your KYC first.')
        return redirect('kyc_form')
    
    context = {
        'kyc': kyc,
        'doctor_profile': doctor_profile,
    }
    
    return render(request, 'authentication/kyc_preview.html', context)