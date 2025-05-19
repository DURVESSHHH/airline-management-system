from django.db import models
from flights.models import Flight

from django.conf import settings 
from django.utils.timezone import now

class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    shift_start = models.TimeField(null=True, blank=True)
    shift_end = models.TimeField(null=True, blank=True)
    assigned_flight = models.ForeignKey('flights.Flight', on_delete=models.SET_NULL, null=True, blank=True)
    completed_tasks = models.IntegerField(default=0)
    pending_tasks = models.IntegerField(default=0)
    STATUS_CHOICES = [
        ('On Duty', 'On Duty'),
        ('Off Duty', 'Off Duty'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Duty')

    shift_status = models.CharField(max_length=50, choices=[
        ('On Duty', 'On Duty'),
        ('Off Duty', 'Off Duty')
    ], default='On Duty')
    
    def __str__(self):
        return f"{self.user.username} - {self.job_title}"

class Task(models.Model):
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Fix
    task_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("In Progress", "In Progress"), ("Completed", "Completed")],
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_name} - {self.staff_member.username} ({self.status})"