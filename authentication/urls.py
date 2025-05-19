from django.urls import path
from django.contrib import admin
from . import views
from .views import overview, fleet_management, add_aircraft, delete_aircraft, revenue_report, send_otp_email, verify_otp, admin_logs, export_logs_csv
from django.contrib.auth import views as auth_views

app_name = 'authentication'  # ✅ Keep this for namespacing

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # ✅ Logout URL is correct
    path('revenue-report/', revenue_report, name='revenue_report'),

    
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('redirect_role_based/', views.redirect_role_based, name='redirect_role_based'),

    # Admin features
    path('overview/', views.overview, name='overview'),
    path("admin-logs/", admin_logs, name="admin_logs"),
    path("export-logs/", export_logs_csv, name="export_logs"),

    # Fleet Management
    path('fleet/', fleet_management, name='fleet_management'),
    path('fleet/add/', add_aircraft, name='add_aircraft'),
    path('fleet/delete/<int:aircraft_id>/', delete_aircraft, name='delete_aircraft'),

    # DO NOT include authentication.urls inside itself!
    path('admin/', admin.site.urls),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    path('destinations/', views.destinations_view, name='destinations'),
    path('travel-guides/', views.travel_guides_view, name='travel_guides'),
    path('travel-insurance/', views.travel_insurance_view, name='travel_insurance'),

    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
