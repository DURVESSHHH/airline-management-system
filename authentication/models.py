from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now
from django.conf import settings  # ✅ Fix circular import
from django.contrib.auth.models import User
import random
import string





class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
        ('Customer', 'Customer'),
    )
    last_login = models.DateTimeField(default=now)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'Admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class RevenueReport(models.Model):
    date = models.DateField(default=now)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    flight_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    service_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    refunds = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    net_revenue = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Revenue Report - {self.date} | Net: ${self.net_revenue}"

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if OTP is valid within 5 minutes"""
        return (now() - self.created_at).seconds < 300  # 5 minutes
    
class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.TextField()
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Show newest logs first

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"