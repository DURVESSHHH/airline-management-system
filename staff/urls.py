from django.urls import path
from . import views
from .views import staff_dashboard

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('add/', views.add_staff, name='add_staff'),
    path('edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('dashboard/', staff_dashboard, name='staff_dashboard'),
    path("update-task/", views.update_task_status, name="update_task"),
    path("get-flight-status/", views.get_flight_status, name="get_flight_status"),
]
