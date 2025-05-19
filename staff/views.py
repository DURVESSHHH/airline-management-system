from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Staff, Task
from django.contrib.auth.hashers import make_password
from authentication.models import CustomUser
from .forms import StaffForm
from flights.models import Flight
from booking.models import Booking
from datetime import datetime

@login_required
def staff_list(request):
    """Display all staff members in the system."""
    staff_members = Staff.objects.all()
    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})


def add_staff(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        job_title = request.POST['job_title']
        shift_start = request.POST['shift_start']
        shift_end = request.POST['shift_end']
        sstatus = request.POST.get('status', 'default_value') 

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('staff:add_staff')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('staff:add_staff')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('staff:add_staff')

        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.role = 'Staff'
        user.save()

        # Create staff profile
        Staff.objects.create(
            user=user,
            job_title=job_title,
            shift_start=shift_start,
            shift_end=shift_end,
            status=sstatus
        )

        messages.success(request, "Staff account created successfully.")
        return redirect('staff:add_staff')

    return render(request, 'staff/add_staff.html')

@login_required
def edit_staff(request, staff_id):
    staff_member = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            return redirect('staff:staff_list')
    else:
        form = StaffForm(instance=staff_member)
    return render(request, 'staff/edit_staff.html', {'form': form})

@login_required
def delete_staff(request, staff_id):
    staff_member = get_object_or_404(Staff, id=staff_id)
    staff_member.delete()
    return redirect('staff:staff_list')

@login_required
def staff_dashboard(request):
    """Fetch staff-related information for the dashboard"""
    
    staff_member = get_object_or_404(Staff, user=request.user)  # Get logged-in staff member

    # Fetch assigned flights for today
    today = datetime.now().date()
    assigned_flight = Flight.objects.filter(assigned_staff=staff_member, departure_time__date=today).first()

    # Fetch completed & pending tasks
    tasks_completed = Task.objects.filter(staff=staff_member, status='completed').count()
    pending_tasks = Task.objects.filter(staff=staff_member, status='pending').count()

    # Fetch training details (replace with actual data from DB)
    training_course = "Safety Refresher"
    training_date = "2025-03-15"
    training_location = "Training Center B"

    # Fetch recent messages/alerts (replace with actual DB queries)
    new_crew_notifications = 2
    schedule_updates = 1
    general_announcements = 3

    # Performance metrics (Replace with real data)
    on_time_performance = 98
    safety_compliance = 100
    customer_feedback = 4.8

    # Flight Status Indicator
    if assigned_flight:
        flight_status = assigned_flight.status
        flight_number = assigned_flight.flight_number
        departure_time = assigned_flight.departure_time
        route = f"{assigned_flight.source} → {assigned_flight.destination}"
    else:
        flight_status = "No Assigned Flight"
        flight_number = "N/A"
        departure_time = "N/A"
        route = "N/A"

    # Define Status Indicators
    status_indicator = "status-good" if flight_status == "On Time" else "status-warning"
    task_status_indicator = "status-warning" if pending_tasks > 0 else "status-good"
    performance_status_indicator = "status-good" if on_time_performance > 90 else "status-warning"
    training_status = "status-warning" if training_course else "status-good"
    messages_status = "status-warning" if new_crew_notifications > 0 else "status-good"

    context = {
        'staff_member_name': staff_member.user.username,
        'shift_status': staff_member.shift_status,
        'flight_status': flight_status,
        'tasks_completed': tasks_completed,
        'flight_number': flight_number,
        'departure_time': departure_time,
        'route': route,
        'status': flight_status,
        'status_indicator': status_indicator,
        'pre_flight_check_status': "Completed",
        'safety_briefing_status': "Pending",
        'documentation_status': "In Progress",
        'task_status_indicator': task_status_indicator,
        'on_time_performance': on_time_performance,
        'safety_compliance': safety_compliance,
        'customer_feedback': customer_feedback,
        'performance_status_indicator': performance_status_indicator,
        'training_course': training_course,
        'training_date': training_date,
        'training_location': training_location,
        'training_status': training_status,
        'new_crew_notifications': new_crew_notifications,
        'schedule_updates': schedule_updates,
        'general_announcements': general_announcements,
        'messages_status': messages_status
    }

    return render(request, 'staff/dashboard.html', context)

@login_required
def update_task_status(request):
    """Allows staff members to update task status."""
    if request.method == "POST":
        task_id = request.POST.get("task_id")  # Get task ID from form
        new_status = request.POST.get("status")  # Get new status

        # Fetch the task from DB
        task = get_object_or_404(Task, id=task_id, staff_member=request.user)

        # Update the status
        task.status = new_status
        task.save()

        return redirect("staff:staff_dashboard")  # Redirect back to dashboard

    return redirect("staff:staff_dashboard")  # In case of GET request

def get_flight_status(request, flight_id):
    """Fetches the latest flight status for staff members"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    context = {
        "flight_number": flight.flight_number,
        "departure_time": flight.departure_time,
        "route": f"{flight.source} → {flight.destination}",
        "status": flight.status,
    }
    
    return render(request, "staff/flight_status.html", context)