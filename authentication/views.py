from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .supabase_client import get_supabase_client
from .models import User, PatientProfile, DoctorProfile
import json

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
        return redirect('home')
    return render(request, 'authentication/patient_login.html')

def doctor_login(request):
    """Doctor login page"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'authentication/doctor_login.html')

@csrf_exempt
@require_http_methods(["POST"])
def auth_callback(request):
    """Handle Supabase authentication callback"""
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        user_type = data.get('user_type')
        
        if not access_token or not user_type:
            return JsonResponse({'error': 'Missing required data'}, status=400)
        
        # Get user info from Supabase
        supabase = get_supabase_client()
        supabase.auth.set_session(access_token, data.get('refresh_token', ''))
        user_response = supabase.auth.get_user(access_token)
        
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
        
        # Create profile based on user type
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
    return render(request, 'authentication/doctor_dashboard.html')