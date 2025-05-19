from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'flight', 'seat_number', 'status', 'booking_date', 'price')
    list_filter = ('status', 'flight')
    search_fields = ('customer__username', 'flight__flight_number')
    actions = ['mark_as_confirmed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')
    mark_as_confirmed.short_description = "Mark selected bookings as Confirmed"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')
    mark_as_cancelled.short_description = "Mark selected bookings as Cancelled"
