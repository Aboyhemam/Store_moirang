from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Review
from django.contrib.auth import get_user_model

User=get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your feedback...'}),
        }
        
class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class ChangeNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class ChangePhoneForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number']

class ChangeAddressForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['address']
    
class EmailForm(forms.Form):
    email = forms.EmailField()

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("new_password")
        pw2 = cleaned_data.get("confirm_password")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match")