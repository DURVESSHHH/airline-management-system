from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Extend UserAdmin for better customization
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'role')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    def has_module_permission(self, request):
        """Only allow superusers to access the admin panel."""
        return request.user.is_superuser

# Register the CustomUser model
admin.site.register(CustomUser, CustomUserAdmin)
