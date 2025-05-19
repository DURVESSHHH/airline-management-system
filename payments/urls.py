from django.urls import path
from . import views
from .views import process_payment, verify_payment, payment_success, payment_failure, payment_cancel, request_refund, manage_refunds, approve_refund, reject_refund

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:booking_id>/', views.process_payment, name='initiate_payment'),
    path("process-payment/<int:booking_id>/", process_payment, name="process_payment"),    
    path('verify/<int:booking_id>/', views.verify_payment, name='verify_payment'),
    path('success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('failure/<int:booking_id>/', views.payment_failure, name='payment_failure'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path("request/<int:booking_id>/", views.request_refund, name="request_refund"),
    path("manage-refunds/", views.manage_refunds, name="manage_refunds"),
    path("approve/<int:refund_id>/", views.approve_refund, name="approve_refund"),
    path("reject/<int:refund_id>/", views.reject_refund, name="reject_refund"),
]
