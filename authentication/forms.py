from django import forms
from .models import DoctorProfile, MedicalRecord

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            'gender', 'date_of_birth', 'specialization', 'license_number',
            'years_of_experience', 'medical_degree', 'additional_qualifications',
            'hospital_affiliation', 'department', 'clinic_address', 'city',
            'state', 'pincode', 'country', 'consultation_fee', 'bio',
            'languages_spoken'
        ]
        widgets = {
            'gender': forms.Select(attrs={'placeholder': 'Select Gender'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'specialization': forms.Select(attrs={'placeholder': 'Select Specialization'}),
            'license_number': forms.TextInput(attrs={'placeholder': 'Medical License Number'}),
            'years_of_experience': forms.NumberInput(attrs={'placeholder': 'Years of Experience'}),
            'medical_degree': forms.TextInput(attrs={'placeholder': 'e.g., MBBS, MD, DM'}),
            'additional_qualifications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional certifications or qualifications'}),
            'hospital_affiliation': forms.TextInput(attrs={'placeholder': 'Hospital/Clinic Name'}),
            'department': forms.TextInput(attrs={'placeholder': 'Department'}),
            'clinic_address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Clinic/Hospital Address'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'Pincode'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'consultation_fee': forms.NumberInput(attrs={'placeholder': 'Consultation Fee (₹)'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description about yourself and your expertise'}),
            'languages_spoken': forms.TextInput(attrs={'placeholder': 'e.g., English, Hindi, Tamil'}),
        }
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and not pincode.isdigit():
            raise forms.ValidationError("Pincode must contain only digits")
        if pincode and len(pincode) != 6:
            raise forms.ValidationError("Pincode must be 6 digits")
        return pincode
    
    def clean_years_of_experience(self):
        years = self.cleaned_data.get('years_of_experience')
        if years and years < 0:
            raise forms.ValidationError("Years of experience cannot be negative")
        if years and years > 60:
            raise forms.ValidationError("Please enter a valid years of experience")
        return years


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['record_type', 'title', 'description', 'file', 'report_date']
        widgets = {
            'record_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-background border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-input text-foreground transition-colors'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-background border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-input text-foreground transition-colors',
                'placeholder': 'e.g., Blood Test Results - Dec 2025'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-background border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-input text-foreground transition-colors',
                'rows': 3,
                'placeholder': 'Optional: Add any notes about this report'
            }),
            'file': forms.FileInput(attrs={
                'class': 'sr-only',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'report_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 bg-background border border-input rounded-md focus:ring-2 focus:ring-ring focus:border-input text-foreground transition-colors'
            }),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            file_ext = file.name.lower().split('.')[-1]
            if f'.{file_ext}' not in allowed_extensions:
                raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed")
        
        return file
