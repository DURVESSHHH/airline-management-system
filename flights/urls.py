from django.urls import path
from . import views

app_name = 'flights'  # ✅ Correct namespace

urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('add/', views.add_flight, name='add_flight'),
    path('edit/<int:flight_id>/', views.edit_flight, name='edit_flight'),
    path('delete/<int:flight_id>/', views.delete_flight, name='delete_flight'),
]
