from django import forms
from .models import Flight, Aircraft

COUNTRIES = [
    ('United States', 'United States'),
    ('Canada', 'Canada'),
    ('United Kingdom', 'United Kingdom'),
    ('France', 'France'),
    ('Germany', 'Germany'),
    ('Japan', 'Japan'),
    ('China', 'China'),
    ('India', 'India'),
    ('Brazil', 'Brazil'),
    ('Russia', 'Russia'),
    ('Australia', 'Australia'),
    ('Italy', 'Italy'),
    ('Spain', 'Spain'),
]

class FlightForm(forms.ModelForm):
    source = forms.ChoiceField(choices=COUNTRIES, widget=forms.Select(attrs={'class': 'form-control'}))
    destination = forms.ChoiceField(choices=COUNTRIES, widget=forms.Select(attrs={'class': 'form-control'}))
    price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Flight
        fields = ['flight_number', 'source', 'destination', 'departure_time', 'arrival_time', 'aircraft', 'status', 'price']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = ['name', 'model', 'capacity', 'status']
