from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, RefundRequest
from booking.models import Booking

@receiver(post_save, sender=Payment)
def update_booking_status_on_payment(sender, instance, created, **kwargs):
    if instance.status == "success":
        instance.booking.status = "Confirmed"
        instance.booking.save()
    elif instance.status == "refunded":
        instance.booking.status = "Refunded"
        instance.booking.save()

@receiver(post_save, sender=RefundRequest)
def process_refund_request(sender, instance, created, **kwargs):
    if instance.status == "processed":
        payment = instance.payment
        payment.status = "refunded"
        payment.save()
