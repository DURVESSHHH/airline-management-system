from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Flight, Aircraft
from .forms import FlightForm, AircraftForm

@login_required
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'flights/flight_list.html', {'flights': flights})

@login_required
def add_flight(request):
    if request.method == "POST":
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("flights:flight_list")
    else:
        form = FlightForm()
    return render(request, "flights/add_flight.html", {"form": form})

@login_required
def edit_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('flights:flight_list')
    else:
        form = FlightForm(instance=flight)
    return render(request, 'flights/edit_flight.html', {'form': form})

@login_required
def delete_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    flight.delete()
    return redirect('flights:flight_list')
