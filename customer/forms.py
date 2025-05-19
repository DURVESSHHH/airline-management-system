from django import forms
from .models import CustomerProfile
from .models import SupportTicket
from .models import SupportMessage
from authentication.models import CustomUser
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number"]

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']

class SupportMessageForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ['message']

from django import forms
from authentication.models import CustomUser

class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']