from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PatientProfile, DoctorProfile, DoctorKYC

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        ('User Type', {'fields': ('user_type', 'supabase_user_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'blood_group')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('gender', 'blood_group')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number', 'is_verified', 'hospital_affiliation')
    search_fields = ('user__username', 'user__email', 'license_number', 'specialization')
    list_filter = ('is_verified', 'specialization', 'department')

@admin.register(DoctorKYC)
class DoctorKYCAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'status', 'submitted_at', 'verified_at')
    search_fields = ('doctor__user__username', 'doctor__user__email', 'license_number_verified', 'full_name')
    list_filter = ('status', 'submitted_at', 'verified_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('doctor', 'full_name', 'date_of_birth', 'gender', 'nationality')
        }),
        ('Contact Information', {
            'fields': ('personal_email', 'mobile_number', 'residential_address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Medical License', {
            'fields': ('license_number_verified', 'license_issuing_authority', 'license_issue_date', 'license_expiry_date', 'license_document')
        }),
        ('Education', {
            'fields': ('medical_degree', 'medical_university', 'graduation_year', 'degree_certificate')
        }),
        ('Professional Information', {
            'fields': ('current_hospital', 'designation', 'department_specialty', 'years_of_practice', 'employment_document')
        }),
        ('Identity Verification', {
            'fields': ('identity_document_type', 'identity_document_number', 'identity_document_file')
        }),
        ('Address Proof', {
            'fields': ('address_proof_type', 'address_proof_file')
        }),
        ('KYC Status', {
            'fields': ('status', 'rejection_reason', 'admin_notes')
        }),
        ('Verification', {
            'fields': ('verified_at', 'verified_by', 'created_at', 'updated_at', 'submitted_at')
        }),
    )
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name() or obj.doctor.user.username
    get_doctor_name.short_description = 'Doctor Name'
    
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('status') == 'approved' and obj.verified_at is None:
            from django.utils import timezone
            obj.verified_at = timezone.now()
            obj.verified_by = request.user.get_full_name() or request.user.username
        super().save_model(request, obj, form, change)