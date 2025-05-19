from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .forms import FlightSearchForm, BookingForm
from .models import Booking
from flights.models import Flight
from customer.models import LoyaltyProgram
from django.utils.timezone import localtime, now as timezone_now


# ------------------------
# FLIGHT SEARCH & BOOKING
# ------------------------

@login_required
def search_flights(request):
    """Allow customers to search for flights and redirect to results."""
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            source = form.cleaned_data['source'].strip().title()  
            destination = form.cleaned_data['destination'].strip().title()
            date = form.cleaned_data['date']

            flights = Flight.objects.filter(
                source__iexact=source,
                destination__iexact=destination,
                departure_time__date=date
            )

            if not flights:
                messages.warning(request, "No flights found for the selected criteria.")

            return redirect(reverse('booking:search_results', kwargs={'source': source, 'destination': destination, 'date': date}))

    else:
        form = FlightSearchForm()

    return render(request, 'booking/search_flights.html', {'form': form})

@login_required
def search_results(request, source, destination, date):
    """Display filtered flight search results."""
    source, destination = source.strip().title(), destination.strip().title()

    if isinstance(date, str):  
        date = datetime.strptime(date, '%Y-%m-%d').date()

    flights = Flight.objects.filter(
        source__iexact=source,
        destination__iexact=destination,
        departure_time__date=date
    )

    return render(request, 'booking/search_results.html', {
        'flights': flights,
        'source': source,
        'destination': destination,
        'date': date
    })

@login_required
def book_flight(request, flight_id):
    """Handles booking for a flight with no seat limit per user"""
    user = request.user  
    flight = get_object_or_404(Flight, id=flight_id)

    # ✅ Fix indentation
    booking = Booking.objects.create(
        seat_number="A1",
        meal_preference="Veg",
        seat_preference="Window",
        additional_requests="None",
        price=flight.price,
        booking_date=timezone_now(),
        status="Pending",
        created_at=timezone_now(),
        user=request.user,
        flight=flight
    )

    messages.success(request, "Flight booked successfully! Proceed to payment.")
    return redirect(reverse('payments:process_payment', kwargs={'booking_id': booking.id}))





# ------------------------
# VIEW BOOKINGS & CONFIRMATION
# ------------------------

@login_required
def view_bookings(request, booking_id=None):
    """View bookings for the logged-in user."""
    user = request.user  # ✅ Get the logged-in user
    bookings = Booking.objects.filter(user=user).order_by('-id', '-created_at', '-booking_date')  # ✅ Use `user`

    if booking_id:
        bookings = Booking.objects.filter(id=booking_id, user=user)  # ✅ Use `user`

    return render(request, 'booking/view_bookings.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    """Delete a booking permanently."""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)

    if booking.status == "Paid":
        messages.error(request, "❌ Cannot delete a paid booking!")
        return redirect("booking:view_bookings")

    booking.delete()
    messages.success(request, "✅ Booking deleted successfully!")
    return redirect("booking:view_bookings")

def booking_confirmation(request, booking_id):
    """Displays the booking confirmation details."""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user != booking.customer and request.user.role != 'Admin':
        messages.error(request, "You are not authorized to view this booking.")
        return redirect('booking:search_flights')

    return render(request, 'booking/confirmation.html', {'booking': booking})

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != "Confirmed":
        messages.error(request, "You cannot cancel this booking.")
        return redirect("booking:view_bookings")

    # Update booking status
    booking.status = "Cancelled"
    booking.save()

    # Redirect to refund request page
    return redirect("payment:request_refund", booking_id=booking.id)




@login_required
def download_booking_pdf(request, booking_id):
    print(f"Generating PDF for Booking ID: {booking_id}")

    # Fetch booking
    booking = get_object_or_404(Booking, id=booking_id)
    print(f"Booking Found: {booking}")
    booking.refresh_from_db()

    # Debug logs
    print(f"Booking Status: {booking.status}")
    print(f"Payment Status: {booking.payment_status}")

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=50, bottomMargin=50, leftMargin=30, rightMargin=30)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    
    # Header style (mimics .header h1)
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Title'],
        fontName='Helvetica-Bold',  # Playfair Display not standard; fallback to Helvetica
        fontSize=18,
        textColor=colors.HexColor('#007bff'),
        spaceAfter=20,
    )
    
    # Normal text style (mimics body text)
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',  # Montserrat not standard; fallback to Helvetica
        fontSize=12,
        textColor=colors.HexColor('#333'),
    )
    
    # Footer style (mimics .footer p)
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.white,
        alignment=1,  # Center
    )

    # Convert datetime to local time
    departure_time = localtime(booking.flight.departure_time).strftime("%Y-%m-%d %I:%M %p")
    arrival_time = localtime(booking.flight.arrival_time).strftime("%Y-%m-%d %I:%M %p")

    # Booking data for table
    data = [
        ["Booking ID:", str(booking.id)],
        ["Customer:", booking.user.username],
        ["Flight Number:", booking.flight.flight_number],
        ["From:", booking.flight.source],
        ["To:", booking.flight.destination],
        ["Departure:", departure_time],
        ["Arrival:", arrival_time],
        ["Seat Number:", booking.seat_number],
        ["Price:", f"${booking.price}"],
        ["Payment Status:", booking.payment_status],
    ]

    # Table styling to match .dashboard-item
    table = Table(data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),  # Header row in blue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),  # Body rows in light gray
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666')),  # Gray grid lines
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    # Build PDF content
    elements.append(Paragraph("SkyHigh Airlines - Booking Confirmation", header_style))
    elements.append(Spacer(1, 20))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for booking with us! ✈️", normal_style))

    # Custom header and footer function
    def add_header_footer(canvas, doc):
        # Header
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 18)
        canvas.setFillColor(colors.HexColor('#007bff'))
        canvas.drawString(doc.leftMargin, doc.pagesize[1] - 30, "SkyHigh Airlines")
        canvas.restoreState()

        # Footer (mimics .footer)
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#333'))
        canvas.rect(0, 0, doc.pagesize[0], 40, fill=1)  # Footer background
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 10)
        footer_text = "© 2025 SkyHigh Airlines Management System. All rights reserved."
        canvas.drawCentredString(doc.pagesize[0] / 2, 15, footer_text)
        canvas.restoreState()

    # Build the document with header/footer
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    # Prepare response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking_{booking.id}.pdf"'

    return response


@login_required
def redeem_points(request, flight_id):
    """Allows customers to use loyalty points for a discount."""
    flight = get_object_or_404(Flight, id=flight_id)
    loyalty, created = LoyaltyProgram.objects.get_or_create(customer=request.user)

    if loyalty.points < 1000:
        messages.error(request, "You need at least 1000 points to redeem a discount.")
        return redirect('booking:book_flight', flight_id=flight.id)

    discount = min(flight.price * 0.1, loyalty.points / 10)
    loyalty.points -= int(discount * 10)
    loyalty.update_tier()
    loyalty.save()

    return redirect('booking:book_flight', flight_id=flight.id)
