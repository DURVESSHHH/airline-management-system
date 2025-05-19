from django.contrib import admin
from .models import CustomerProfile
from .models import SupportTicket , SupportMessage
from .models import LoyaltyProgram

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user' , 'phone' , 'loyalty_points')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('customer', 'subject', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'timestamp')

@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'tier')
    list_filter = ('tier',)