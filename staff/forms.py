from django import forms
from .models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'job_title', 'shift_start', 'shift_end']
