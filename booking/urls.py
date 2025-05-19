from django.urls import path
from . import views
from .views import cancel_booking, booking_confirmation, view_bookings, delete_booking, download_booking_pdf, search_flights, search_results, book_flight

app_name = 'booking'

urlpatterns = [
    path('search/', views.search_flights, name='search_flights'),  # ✅ Shows the search page
    path('results/<str:source>/<str:destination>/<str:date>/', views.search_results, name='search_results'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),  
    path("cancel-booking/<int:booking_id>/", cancel_booking, name="cancel_booking"),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),  # ✅ Confirmation page
    path('view-bookings/', view_bookings, name='view_bookings'),  # ✅ Ensure this exists

    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),  # ✅ New delete booking URL
    path('download/<int:booking_id>/', views.download_booking_pdf, name='download_booking_pdf'),  # ✅ Download booking PDF
]
