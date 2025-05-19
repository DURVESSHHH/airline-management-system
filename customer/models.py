from django.db import models
from django.utils.timezone import now
from django.conf import settings  # ✅ Fix circular import
from authentication.models import CustomUser

class CustomerProfile(models.Model):
    """Stores additional details for customers"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Use this instead of direct import
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Customer'}
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Profile"

    def calculate_loyalty_points(self):
        """Calculate points based on completed bookings (1 point per $10 spent)."""
        from booking.models import Booking  # ✅ FIX: Import inside method to avoid circular import
        bookings = Booking.objects.filter(customer=self.user, status='Confirmed')
        total_spent = sum(booking.price for booking in bookings)
        self.loyalty_points = total_spent // 10
        self.save()


class SupportTicket(models.Model):
    """Tracks customer support requests"""
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ Fix circular import
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Customer'}
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True, null=True)  # Admin response

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class SupportMessage(models.Model):
    """Handles support ticket messages"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Fix circular import
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} on Ticket #{self.ticket.id}"


class LoyaltyProgram(models.Model):
    """Loyalty program for rewarding customers"""
    TIER_CHOICES = [
        ('Bronze', 'Bronze'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]

    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Fix circular import
        on_delete=models.CASCADE,
        related_name='loyalty'
    )
    points = models.IntegerField(default=0)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='Bronze')

    def update_tier(self):
        """Automatically updates the loyalty tier based on points."""
        if self.points >= 5000:
            self.tier = 'Platinum'
        elif self.points >= 2500:
            self.tier = 'Gold'
        elif self.points >= 1000:
            self.tier = 'Silver'
        else:
            self.tier = 'Bronze'
        self.save()

    def __str__(self):
        return f"{self.customer.username} - {self.tier} ({self.points} points)"


class Feedback(models.Model):
    """Customer feedback on flights and service"""
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ Fix circular import
        on_delete=models.CASCADE,
        related_name='customer_feedback'
    )
    comment = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Feedback from {self.customer.username} - {self.rating}"

class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # ✅ Ensure this field exists
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name()