from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
from django import forms


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20, help_text='Required.')

    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name')
        
    def clean(self):
       email = self.cleaned_data.get('email')
       if User.objects.filter(email=email).exists():
           raise ValidationError("Email already exists")
       return self.cleaned_data
       


class PersonalDetailsForm(forms.Form):
    
    email = forms.CharField(max_length=100, help_text='Required.')
    first_name = forms.CharField(max_length=100, help_text='Required.')
    last_name = forms.CharField(max_length=100, help_text='Required.')
    phone = forms.CharField(max_length=20, help_text='Required.')
    


class ShippingDetailsForm(forms.Form):
    
    address1 = forms.CharField(max_length=100, help_text='Required.')
    address2 = forms.CharField(max_length=100)
    
    
    
class PaymentDetailsForm(forms.Form):
    payment_method_nonce = forms.CharField(max_length=1000, widget=forms.widgets.HiddenInput, required=True, help_text='Required.')
    
