from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.db import models
from django.db.models import Sum
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from authentication.models import OTP, AuditLog, CustomUser
from django.utils import timezone
from booking.models import Booking
from staff.models import Staff
from flights.models import Aircraft, Flight
from flights.forms import AircraftForm
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.db.models import Sum, Count, Avg
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import RevenueReport
from decimal import Decimal
import csv
import random

from customer.models import CustomerProfile, Feedback, Customer # ✅ Use the correct model name

def home(request):
    """Landing page view."""
    return render(request, 'authentication/base.html')


def register(request):
    """Handles user registration (only for Customers)."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'Customer'  # Force role to be Customer
            user.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('authentication:customer_dashboard')  # Redirect to customer dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/registration.html', {'form': form})


def login_view(request):
    """Handles user login and redirects based on role."""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        remember_me = request.POST.get('remember')

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # ✅ Set session expiry based on 'Remember Me'
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 7)  # 7 days
            else:
                request.session.set_expiry(0)  # Browser close = Logout

            # ✅ Use namespaced URL names instead of hardcoded paths
            if user.is_superuser or user.role == 'Admin':
                return redirect('authentication:admin_dashboard')
            elif user.role == 'Staff':
                return redirect('staff:staff_dashboard')
            else:
                return redirect('authentication:customer_dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'authentication/login.html')

def redirect_role_based(user):
    """Redirect users to their respective dashboards based on their role."""
    if user.role == 'Admin':
        return redirect('authentication:admin_dashboard')
    elif user.role == 'Staff':
        return redirect('staff:staff_dashboard')  # Corrected to 'staff:staff_dashboard'
    elif user.role == 'Customer':
        return redirect('authentication:customer_dashboard')
    return redirect('home')



@login_required
def admin_dashboard(request):
    """Admin Dashboard - Displays key statistics."""
    today = datetime.today().date()

    # ✅ Flight Statistics
    total_flights = Flight.objects.filter(departure_time__date=today).count()
    delayed_flights = Flight.objects.filter(status="Delayed").count()
    cancelled_flights = Flight.objects.filter(status="Cancelled").count()
    
    on_time_performance = round(((total_flights - delayed_flights) / total_flights) * 100, 2) if total_flights > 0 else 100

    # ✅ Staff Management
    total_staff = Staff.objects.count()
    on_duty_staff = Staff.objects.filter(shift_status="On Duty").count()  # Ensure correct field
    off_duty_staff = total_staff - on_duty_staff

    # ✅ Customer Insights
    total_customers = Customer.objects.count()
    new_signups = Customer.objects.filter(user__date_joined__gte=today - timedelta(days=30)).count()
    active_bookings = Booking.objects.filter(status="Confirmed").count()

    # ✅ Revenue Overview
    todays_revenue = RevenueReport.objects.filter(date=today).aggregate(total=Sum('total_revenue'))['total'] or 0
    monthly_revenue = RevenueReport.objects.filter(date__month=today.month).aggregate(total=Sum('total_revenue'))['total'] or 0
    yearly_revenue = RevenueReport.objects.filter(date__year=today.year).aggregate(total=Sum('total_revenue'))['total'] or 0

    # ✅ Fleet Management
    total_aircraft = Flight.objects.values('aircraft').distinct().count()  
    aircraft_in_service = Flight.objects.filter(status="Operational").count()
    aircraft_under_maintenance = Flight.objects.filter(status="Maintenance").count()

    # ✅ Recent Alerts (Dummy Data)
    recent_alerts = [
        "Flight 102 delayed due to weather.",
        "New customer complaint received.",
        "Aircraft A320 undergoing maintenance."
    ]

    context = {
        "total_flights": total_flights,
        "on_time_performance": on_time_performance,
        "delayed_flights": delayed_flights,
        "cancelled_flights": cancelled_flights,
        "total_staff": total_staff,
        "on_duty_staff": on_duty_staff,
        "off_duty_staff": off_duty_staff,
        "total_customers": total_customers,
        "new_signups": new_signups,
        "active_bookings": active_bookings,
        "todays_revenue": todays_revenue,
        "monthly_revenue": monthly_revenue,
        "yearly_revenue": yearly_revenue,
        "total_aircraft": total_aircraft,
        "aircraft_in_service": aircraft_in_service,
        "aircraft_under_maintenance": aircraft_under_maintenance,
        "recent_alerts": recent_alerts,
    }

    return render(request, 'authentication/admin_dashboard.html', context)


def customer_dashboard(request):
    customer = request.user
    
    # ✅ Query bookings for the current user with future flights
    upcoming_bookings = Booking.objects.filter(
        user=request.user,  # ✅ Use `user` instead of `customer`
        flight__departure_time__gte=timezone.now()
    ).select_related('flight')

    # ✅ Get unique flights using a set
    upcoming_flights = list({booking.flight.id: booking.flight for booking in upcoming_bookings}.values())

    special_offers = ["10% off next flight", "Free upgrade offer"]
    recent_activities = ["Booked flight XYZ on Mar 15", "Submitted ticket #123"]

    points_balance = getattr(customer, 'points_balance', 0)
    next_tier_points = getattr(customer, 'next_tier_points', 5000) or 5000
    loyalty_progress_percentage = (points_balance / next_tier_points) * 100 if next_tier_points > 0 else 0

    context = {
        'upcoming_flights': upcoming_flights,
        'customer': customer,
        'special_offers': special_offers,
        'recent_activities': recent_activities,
        'loyalty_progress_percentage': loyalty_progress_percentage,
    }
    print("Upcoming Flights:", upcoming_flights)  # Debug output
    return render(request, 'authentication/customer_dashboard.html', context)


@login_required
def logout_view(request):
    """Handles user logout."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('authentication:login')


@login_required
def overview(request):
    """Admin dashboard overview with real-time data."""
    
    total_flights = Flight.objects.count()
    active_bookings = Booking.objects.filter(status='Confirmed').count()
    total_revenue = Booking.objects.filter(status='Confirmed').aggregate(Sum('price'))['price__sum'] or 0
    
    customer_satisfaction = Feedback.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    customer_satisfaction = round(customer_satisfaction * 20)  # Convert rating to percentage

    context = {
        'total_flights': total_flights,
        'active_bookings': active_bookings,
        'total_revenue': total_revenue,
        'customer_satisfaction': customer_satisfaction
    }

    return render(request, 'authentication/overview.html', context)


@login_required
def fleet_management(request):
    """View all aircraft in the fleet"""
    aircrafts = Aircraft.objects.all()
    form = AircraftForm()

    return render(request, 'authentication/fleet_management.html', {
        'aircrafts': aircrafts,
        'form': form
    })

@login_required
def add_aircraft(request):
    """Add a new aircraft"""
    if request.method == 'POST':
        form = AircraftForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('authentication:fleet_management')  # Ensure URL name matches
    return redirect('authentication:fleet_management')

@login_required
def delete_aircraft(request, aircraft_id):
    """Delete an aircraft"""
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    aircraft.delete()
    return redirect('authentication:fleet_management')

def is_admin(user):
    return user.is_authenticated and user.role == "Admin"


def revenue_report(request):
    # Get today's date
    today = now().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Fetch revenue data from the database (Assuming Booking has 'created_at' field)
    todays_bookings = Booking.objects.filter(created_at__date=today)
    monthly_bookings = Booking.objects.filter(created_at__date__gte=month_start)
    yearly_bookings = Booking.objects.filter(created_at__date__gte=year_start)

    # Calculate revenue (Replace 'total_price' with 'price')
    todays_revenue = todays_bookings.aggregate(Sum('price'))['price__sum'] or  Decimal('0.0')
    monthly_revenue = monthly_bookings.aggregate(Sum('price'))['price__sum'] or  Decimal('0.0')
    yearly_revenue = yearly_bookings.aggregate(Sum('price'))['price__sum'] or  Decimal('0.0')
    factor = Decimal('0.8')

    # Adjust flight revenue (80% of total revenue)
    flight_todays_revenue = todays_revenue * factor
    flight_monthly_revenue = monthly_revenue * factor
    flight_yearly_revenue = yearly_revenue * factor

    # Get flights for today's bookings
    revenue_data = []
    for booking in todays_bookings:
        if booking.flight:
            revenue_data.append({
                'date': today,
                'flight_number': booking.flight.flight_number,
                'route': f"{booking.flight.source} - {booking.flight.destination}",
                'revenue': booking.price * 0.8,  # Adjusted per booking
                'payment_status': booking.payment_status,
            })

    context = {
        'todays_revenue': flight_todays_revenue,
        'monthly_revenue': flight_monthly_revenue,
        'yearly_revenue': flight_yearly_revenue,
        'revenue_data': revenue_data,
    }
    return render(request, 'authentication/revenue_report.html', context)


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp_code):
    subject = 'SkyHigh Airlines - OTP for Password Reset'
    message = f'Your OTP code is: {otp_code}. It will expire in 2 minutes.'
    from_email = 'SkyHigh <noreply@skyhigh.com>'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        method = request.POST.get('otp_method')

        try:
            user = CustomUser.objects.get(username=username, email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with these details.')
            return redirect('authentication:forgot_password')

        otp_code = generate_otp()
        OTP.objects.create(user=user, otp_code=otp_code)

        if method == 'email':
            send_otp_email(user.email, otp_code)
        # Future: SMS can be integrated here

        AuditLog.objects.create(user=user, action='Requested OTP for password reset')
        messages.success(request, 'OTP sent! Check your email.')
        request.session['username_for_otp'] = username
        return redirect('authentication:verify_otp')

    return render(request, 'authentication/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        username = request.session.get('username_for_otp') or request.POST.get('username')
        otp_input = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        try:
            user = CustomUser.objects.get(username=username)
            latest_otp = OTP.objects.filter(user=user).latest('created_at')

            if not latest_otp.is_valid():
                messages.error(request, 'OTP has expired.')
                return redirect('authentication:forgot_password')

            if latest_otp.otp_code != otp_input:
                AuditLog.objects.create(user=user, action='Failed OTP attempt')
                messages.error(request, 'Invalid OTP.')
                return redirect('authentication:verify_otp')

            user.password = make_password(new_password)
            user.save()
            OTP.objects.filter(user=user).delete()  # Clean up
            AuditLog.objects.create(user=user, action='OTP Verified and Password Reset')

            messages.success(request, 'Password updated. Login now.')
            return redirect('authentication:login')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('authentication:verify_otp')

    return render(request, 'authentication/verify_otp.html')


@login_required
def admin_logs(request):
    if not request.user.is_staff:
        return render(request, "authentication/access_denied.html")  # Restrict access

    logs = AuditLog.objects.all()

    # ✅ Filtering based on user and action (if requested)
    user_filter = request.GET.get("user")
    action_filter = request.GET.get("action")

    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)

    return render(request, "authentication/admin_logs.html", {"logs": logs})

def export_logs_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Timestamp", "User", "Action", "Details"])

    logs = AuditLog.objects.all()
    for log in logs:
        writer.writerow([log.timestamp, log.user.username if log.user else "Anonymous", log.action, log.details])

    return response


from django.shortcuts import render

def destinations_view(request):
    return render(request, 'authentication/destinations.html')

def travel_guides_view(request):
    return render(request, 'authentication/travel_guides.html')

def travel_insurance_view(request):
    return render(request, 'authentication/travel_insurance.html')


