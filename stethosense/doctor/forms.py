from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DoctorProfile

class DoctorRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ('name', 'phone', 'Specialisation', 'City', 'Registration_Number', 'Registration_Council', 'Registration_year', 'Degree', 'College', 'Year_of_completion', 'Medical_registration_proof', 'Current_place_of_work', 'Gender', 'Profile_pic', 'Aadhar_Number')
        widgets = {
            'Medical_registration_proof': forms.ClearableFileInput(attrs={'multiple': False}),
            'Profile_pic': forms.ClearableFileInput(),
        }

    def clean_Medical_registration_proof(self):
        proof = self.cleaned_data.get('Medical_registration_proof')
        if proof and len(proof) > 5:  # Limiting the number of proofs to 5
            raise forms.ValidationError("You can only upload up to 5 medical registration proofs.")
        return proof
