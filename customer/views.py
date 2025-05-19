from .models import CustomerProfile
from booking.models import Booking
from .forms import CustomerProfileForm
from .models import SupportTicket
from .forms import SupportTicketForm
from .forms import SupportMessageForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.models import CustomUser
from .forms import CustomerUpdateForm
from .models import LoyaltyProgram


def view_customers(request):
    """Admin view to list all customers"""
    if request.user.role != 'Admin':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('authentication:admin_dashboard')

    customers = CustomUser.objects.filter(role='Customer')
    return render(request, 'customer/view_customers.html', {'customers': customers})

def edit_customer(request, customer_id):
    """Admin view to edit customer details."""
    if request.user.role != 'Admin':
        messages.error(request, "You are not authorized to edit customers.")
        return redirect('customer:view_customers')

    customer = get_object_or_404(CustomUser, id=customer_id)

    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer details updated successfully.")
            return redirect('customer:view_customers')
    else:
        form = CustomerUpdateForm(instance=customer)

    return render(request, 'customer/edit_customer.html', {'form': form, 'customer': customer})


def delete_customer(request, customer_id):
    """Admin view to delete a customer"""
    if request.user.role != 'Admin':
        messages.error(request, "You are not authorized to delete customers.")
        return redirect('admin_dashboard')

    customer = get_object_or_404(CustomUser, id=customer_id)
    customer.delete()
    messages.success(request, "Customer deleted successfully.")
    return redirect('customer:view_customers')

@login_required
def customer_profile(request):
    user = request.user  # Get logged-in user
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("customer:customer_profile")  # Redirect after updating
        else:
            messages.error(request, "Error updating profile. Please check your input.")
    else:
        form = CustomerProfileForm(instance=user)

    # Fetch latest profile data
    profile = user  # Assuming there's a OneToOneField between User and Profile
    return render(request, "customer/profile.html", {
        "form": form,
        "user": user, 
        "profile": profile,
    })

@login_required
def travel_history(request):
    if request.user.role != 'Customer':
        return redirect('login')

    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'customer/travel_history.html', {'bookings': bookings})

@login_required
def submit_ticket(request):
    if request.user.role != 'Customer':
        return redirect('login')

    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.customer = request.user
            ticket.save()
            return redirect('customer:view_tickets')
    else:
        form = SupportTicketForm()
    
    return render(request, 'customer/submit_ticket.html', {'form': form})


def view_tickets(request):
    """Customer views their submitted tickets"""
    if request.user.role != 'Customer':
        return redirect('login')

    tickets = SupportTicket.objects.filter(customer=request.user)
    return render(request, 'customer/view_tickets.html', {'tickets': tickets})


def manage_tickets(request):
    if request.user.role != 'Admin':
        return redirect('login')

    tickets = SupportTicket.objects.all()
    return render(request, 'customer/manage_tickets.html', {'tickets': tickets})


def respond_ticket(request, ticket_id):
    if request.user.role != 'Admin':
        return redirect('login')

    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    if request.method == 'POST':
        response = request.POST.get('response')
        ticket.response = response
        ticket.status = 'Resolved'
        ticket.save()
        return redirect('customer:manage_tickets')

    return render(request, 'customer/respond_ticket.html', {'ticket': ticket})

def ticket_detail(request, ticket_id):
    """View ticket details and message history"""
    # Update the query to use 'customer' instead of 'user'
    ticket = get_object_or_404(SupportTicket, id=ticket_id, customer=request.user)
    messages = ticket.messages.all()

    if request.method == 'POST':
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            return redirect('customer:ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportMessageForm()

    return render(request, 'customer/ticket_detail.html', {'ticket': ticket, 'messages': messages, 'form': form})


def admin_ticket_detail(request, ticket_id):
    """Admin view to respond to tickets"""
    if request.user.role != 'Admin':
        return redirect('login')

    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    messages = ticket.messages.all()

    if request.method == 'POST':
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            return redirect('customer:admin_ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportMessageForm()

    return render(request, 'customer/admin_ticket_detail.html', {'ticket': ticket, 'messages': messages, 'form': form}) 

@login_required
def view_loyalty_points(request):
    """Displays loyalty points and tier for the logged-in customer."""
    loyalty, created = LoyaltyProgram.objects.get_or_create(customer=request.user)
    return render(request, 'customer/loyalty_program.html', {'loyalty': loyalty})  