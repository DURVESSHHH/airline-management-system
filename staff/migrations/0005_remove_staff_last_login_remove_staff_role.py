# Generated by Django 5.1.7 on 2025-04-21 23:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_staff_completed_tasks_staff_pending_tasks_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='role',
        ),
    ]
