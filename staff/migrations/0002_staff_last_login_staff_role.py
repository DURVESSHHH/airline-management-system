# Generated by Django 5.1.7 on 2025-04-21 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='last_login',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='role',
            field=models.CharField(choices=[('Pilot', 'Pilot'), ('Ground Staff', 'Ground Staff'), ('Cabin Crew', 'Cabin Crew')], default=1, max_length=50),
            preserve_default=False,
        ),
    ]
