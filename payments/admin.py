from django.contrib import admin
from .models import Payment, RefundRequest

admin.site.register(Payment)
admin.site.register(RefundRequest)
