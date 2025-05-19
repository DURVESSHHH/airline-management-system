from django.db import models

class Aircraft(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100, default="Unknown Model")
    capacity = models.IntegerField()
    status = models.CharField(
        max_length=50,
        choices=[('Operational', 'Operational'), ('Maintenance', 'Maintenance')],
        default='Operational'
    )

    def __str__(self):
        return f"{self.name} ({self.model})"

class Flight(models.Model):
    flight_number = models.CharField(max_length=10, unique=True)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField(default=100)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('Scheduled', 'Scheduled'),
            ('Delayed', 'Delayed'),
            ('Cancelled', 'Cancelled')
        ],
        default='Scheduled'
    )

    assigned_staff = models.ForeignKey(
        'staff.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_flights'
    )

    def __str__(self):
        return f"{self.flight_number} - {self.source} to {self.destination}"
