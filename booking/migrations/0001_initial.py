# Generated by Django 5.1.7 on 2025-04-22 00:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('flights', '0003_flight_assigned_staff'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('seat_number', models.CharField(max_length=10)),
                ('meal_preference', models.CharField(choices=[('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian'), ('vegan', 'Vegan'), ('none', 'No Meal')], default='none', max_length=20)),
                ('seat_preference', models.CharField(choices=[('window', 'Window'), ('aisle', 'Aisle'), ('middle', 'Middle'), ('none', 'No Preference')], default='none', max_length=20)),
                ('additional_requests', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending Payment'), ('Paid', 'Paid'), ('Failed', 'Payment Failed')], default='Pending', max_length=10)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=255, null=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=255, null=True)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flights.flight')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
