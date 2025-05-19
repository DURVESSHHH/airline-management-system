from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'shift_start', 'shift_end')
    search_fields = ('user__username', 'job_title')
    list_filter = ('job_title',)
    fieldsets = (
        (None, {
            'fields': ('user', 'job_title', 'shift_start', 'shift_end')
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('user', 'job_title', 'shift_start', 'shift_end')
        }),
    )