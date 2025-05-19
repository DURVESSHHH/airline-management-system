from django.urls import path
from . import views

app_name = 'customer'  # Namespace for URLs

urlpatterns = [
    # Customer-side URLs
     path('loyalty/', views.view_loyalty_points, name='view_loyalty_points'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('travel_history/', views.travel_history, name='travel_history'),

    # Customer-side URLs
    path('support/submit/', views.submit_ticket, name='submit_ticket'),
    path('support/tickets/', views.view_tickets, name='view_tickets'),
    path('support/ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # Admin-side URLs
    path('admin/manage-tickets/', views.manage_tickets, name='manage_tickets'),
    path('admin/ticket/<int:ticket_id>/', views.admin_ticket_detail, name='admin_ticket_detail'),
    

    # Customer management
    path('', views.view_customers, name='view_customers'),  # List all customers
    path('edit/<int:customer_id>/', views.edit_customer, name='edit_customer'),  # Edit customer
    path('delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),  # Delete customer
]
