from django import forms
from .models import Booking
from flights.models import Flight  # ✅ Ensure correct Flight model is used

COUNTRIES = [
    ('United States', 'United States'),
    ('Canada', 'Canada'),
    ('United Kingdom', 'United Kingdom'),
    ('France', 'France'),
    ('Germany', 'Germany'),
    ('Japan', 'Japan'),
    ('China', 'China'),  # ✅ Fixed
    ('India', 'India'),
    ('Brazil', 'Brazil'),  # ✅ Fixed
    ('Russia', 'Russia'),  # ✅ Fixed
    ('Australia', 'Australia'),
    ('Italy', 'Italy'),
    ('Spain', 'Spain'),
]

class FlightSearchForm(forms.Form):
    source = forms.ChoiceField(choices=COUNTRIES, required=True)
    destination = forms.ChoiceField(choices=COUNTRIES, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)  # ✅ Fix date format


class BookingForm(forms.ModelForm):
    MEAL_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('gluten-free', 'Gluten-Free'),
    ]

    SEAT_CHOICES = [
        ('window', 'Window'),
        ('aisle', 'Aisle'),
        ('middle', 'Middle'),
    ]

    seat_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Seat Number'})
    )
    meal_preference = forms.ChoiceField(
        choices=Booking.MEAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    seat_preference = forms.ChoiceField(
        choices=Booking.SEAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    additional_requests = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests'}),
        required=False
    )

    class Meta:
        model = Booking
        fields = ['seat_number', 'meal_preference', 'seat_preference', 'additional_requests']
