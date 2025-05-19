from django.db import models
from django.conf import settings 
from django.utils import timezone
from authentication.models import CustomUser  # ✅ Import CustomUser
from django.contrib.auth.models import User  # ✅ Import User model
from django.apps import apps  



class Booking(models.Model):
    MEAL_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('none', 'No Meal')
    ]

    SEAT_CHOICES = [
        ('window', 'Window'),
        ('aisle', 'Aisle'),
        ('middle', 'Middle'),
        ('none', 'No Preference')
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending Payment"),
        ("Paid", "Paid"),
        ("Failed", "Payment Failed"),
    ]

    id = models.AutoField(primary_key=True)

    # ✅ Keep only one customer field
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    flight = models.ForeignKey('flights.Flight', on_delete=models.CASCADE)
    
    seat_number = models.CharField(max_length=10)
    meal_preference = models.CharField(max_length=20, choices=MEAL_CHOICES, default='none')
    seat_preference = models.CharField(max_length=20, choices=SEAT_CHOICES, default='none')
    
    additional_requests = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    booking_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")

    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="Pending")
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)  
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)  # ✅ Added for tracking successful payments

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.flight.flight_number}"