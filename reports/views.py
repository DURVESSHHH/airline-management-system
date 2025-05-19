import datetime
import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from booking.models import Booking

@login_required
def report_detail(request):
    # Get today's date
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    # Fix: Use 'booking_date' instead of 'date'
    todays_revenue = Booking.objects.filter(payment_status='Paid', booking_date=today).aggregate(Sum('price'))['price__sum'] or 0.00
    monthly_revenue = Booking.objects.filter(payment_status='Paid', booking_date__month=current_month).aggregate(Sum('price'))['price__sum'] or 0.00
    yearly_revenue = Booking.objects.filter(payment_status='Paid', booking_date__year=current_year).aggregate(Sum('price'))['price__sum'] or 0.00

    # Revenue Data for Table
    revenue_data = Booking.objects.filter(payment_status='Paid').values(
        'booking_date', 'flight__flight_number', 'flight__source', 'flight__destination', 'price', 'payment_status'
    )

    # Format data
    formatted_data = [
        {
            "date": entry['booking_date'],
            "flight_number": entry['flight__flight_number'],
            "route": f"{entry['flight__source']} → {entry['flight__destination']}",  # Fix: Changed 'origin' to 'source'
            "revenue": entry['price'],
            "payment_status": entry['payment_status']
        }
        for entry in revenue_data
    ]

    return render(request, 'reports/report_detail.html', {
        'todays_revenue': todays_revenue,
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        'revenue_data': formatted_data,
    })

@login_required
def download_csv_report(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="revenue_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Flight Number", "Route", "Revenue", "Payment Status"])

    bookings = Booking.objects.filter(payment_status='Paid')
    for booking in bookings:
        writer.writerow([
            booking.booking_date.strftime("%Y-%m-%d"),  # Fix: Using 'booking_date'
            booking.flight.flight_number,
            f"{booking.flight.source} → {booking.flight.destination}",  # Fix: Changed 'origin' to 'source'
            booking.price,
            booking.payment_status
        ])

    return response
