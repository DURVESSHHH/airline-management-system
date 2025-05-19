from django.urls import path, include
from django.contrib import admin
from authentication import views



app_name = 'airline_management'


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('customer/', include('customer.urls', namespace='customer')),
    path('flights/', include('flights.urls', namespace='flights')),
    path('staff/', include('staff.urls', namespace='staff')),
    path('reports/', include('reports.urls')),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('payments/', include('payments.urls', namespace='payments')),
]
