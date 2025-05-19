from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Payment, RefundRequest
from django.contrib.auth.decorators import login_required
from .forms import RefundRequestForm
from booking.models import Booking
import razorpay
from django.conf import settings
from django.http import JsonResponse  # ✅ Import this
from django.views.decorators.csrf import csrf_exempt  # ✅ Import
import json  # ✅ Import json module
import hmac
import hashlib
import logging
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError



# Initialize Razorpay Client
logger = logging.getLogger(__name__)  # Use the module name as the logger name

def process_payment(request, booking_id):
    logger.debug(f"Processing payment for booking_id: {booking_id}")

    booking = get_object_or_404(Booking, id=booking_id)
    user = getattr(booking, "user", None)

    if not user:
        logger.warning("User not found for this booking")
        return JsonResponse({"error": "User not found for this booking"}, status=400)

    try:
        amount = int(float(booking.price) * 100)
    except ValueError:
        logger.error("Invalid price format encountered")
        return JsonResponse({"error": "Invalid price format"}, status=400)

    # Fetch or create payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={"user": user, "amount": booking.price, "status": "pending"}
    )

    if created:
        logger.info(f"New Payment instance created for booking: {booking.id}")
    else:
        logger.info(f"Existing Payment instance retrieved for booking: {booking.id}")

    # If an order already exists, use it
    if payment.razorpay_order_id:
        logger.info(f"Using existing Razorpay Order ID: {payment.razorpay_order_id}")
        order_id = payment.razorpay_order_id
    else:
        # Create a new order in Razorpay
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_data = {"amount": amount, "currency": "INR", "payment_capture": 1}

        try:
            order = razorpay_client.order.create(order_data)
            order_id = order["id"]

            # Automatically save order ID
            payment.razorpay_order_id = order_id
            payment.save(update_fields=["razorpay_order_id"])  # ✅ Saves only this field
            logger.info(f"New Razorpay Order Created and Saved: {order_id}")

        except razorpay.errors.AuthenticationError:
            logger.error("Razorpay Authentication Failed! Check API Keys.")
            return JsonResponse({"error": "Payment gateway authentication failed"}, status=401)
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay Error: {str(e)}")
            return JsonResponse({"error": "Invalid request to Razorpay"}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error while creating Razorpay order: {str(e)}")
            return JsonResponse({"error": "Payment processing failed"}, status=500)

    return render(request, "payments/process_payment.html", {
        "booking": booking,
        "payment": payment,
        "amount": amount / 100,  # Convert back to INR for display
        "order_id": order_id,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

def payment_cancel(request):
    return render(request, 'payments/payment_cancel.html')

@csrf_exempt
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = get_object_or_404(Payment, booking=booking)

    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        # ⚠️ Verify Signature
        try:
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }

            # ✅ Signature Verification
            razorpay_client.utility.verify_payment_signature(params_dict)

            # ✅ Update Payment in DB
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_order_id = razorpay_order_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "success"
            payment.save()

            # Optional: You can also mark the booking as confirmed if needed

            messages.success(request, "Payment verified and saved successfully.")
        except SignatureVerificationError:
            payment.status = "failed"
            payment.save()
            messages.error(request, "Payment verification failed.")
            return render(request, "payments/payment_failed.html", {"booking": booking})

    return render(request, "payments/payment_success.html", {"booking": booking})

def payment_failure(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = Payment.objects.filter(booking=booking).first()

    return render(request, "payments/payment_failure.html", {"payment": payment, "booking": booking})

def confirm_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        confirm_payment = request.POST.get("confirm_payment")

        if confirm_payment == "yes":
            return redirect("payments:process_payment", booking_id=booking.id)  # Redirect to process payment

        elif confirm_payment == "no":
            return redirect("booking:view_bookings", booking_id=booking.id)  # Redirect to bookings

    return render(request, "payments/confirm_payment.html", {"booking": booking})




def verify_payment(request, booking_id):
    if request.method == "POST":
        data = json.loads(request.body)

        # ✅ Ensure these values are received
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            print("❌ Missing Payment Response Data:", data)  # Debugging
            return JsonResponse({"status": "failure"}, status=400)

        # ✅ Generate Signature
        secret = settings.RAZORPAY_KEY_SECRET
        generated_signature = hmac.new(
            key=bytes(secret, "utf-8"),
            msg=bytes(razorpay_order_id + "|" + razorpay_payment_id, "utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        if generated_signature == razorpay_signature:
            print("✅ Payment Verified for Booking:", booking_id)  # Debugging
            Booking.objects.filter(id=booking_id).update(payment_status="Paid")
            return JsonResponse({"status": "success"})
        else:
            print("❌ Payment Verification Failed:", generated_signature)  # Debugging
            return JsonResponse({"status": "failure"}, status=400)

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=("YOUR_RAZORPAY_KEY", "YOUR_RAZORPAY_SECRET"))

@login_required
def request_refund(request, booking_id):
    print(f"🔍 Received request for refund on booking ID: {booking_id}")

    # Check if a payment exists for this booking
    payment = Payment.objects.filter(booking__id=booking_id).first()
    
    if not payment:
        messages.error(request, "No payment found for this booking.")
        return redirect("payments:payment_failure", booking_id=booking_id)

    print(f"✅ Payment found: {payment}")

    if request.method == "POST":
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund_request, created = RefundRequest.objects.get_or_create(
                payment=payment,
                user=request.user,
                defaults={"reason": form.cleaned_data["reason"], "status": "pending"},
            )
            if not created:
                messages.warning(request, "Refund request already exists for this booking.")
                return redirect("payments:payment_success", booking_id=booking_id)
            
            messages.success(request, "Refund request submitted successfully.")
            return redirect("payments:payment_success", booking_id=booking_id)
    
    form = RefundRequestForm()
    return render(request, "payments/request_refund.html", {"form": form, "payment": payment})

@login_required
def manage_refunds(request):
    refunds = RefundRequest.objects.filter(status="pending")
    
    # Debugging: Log data to console
    for refund in refunds:
        print(f"Refund ID: {refund.id}, Booking ID: {refund.payment.booking.id}, Status: {refund.status}")

    return render(request, "payments/manage_refunds.html", {"refunds": refunds})

@login_required
def approve_refund(request, refund_id):
    if not request.user.is_staff:
        messages.error(request, "Access Denied!")
        return redirect("booking:view_bookings")

    refund = get_object_or_404(RefundRequest, id=refund_id, status="pending")
    payment = refund.payment

    # ✅ Debug: Check Payment ID
    if not payment.razorpay_payment_id:
        messages.error(request, f"Refund cannot be processed — no Razorpay payment ID found for Payment #{payment.id}.")
        logger.warning(f"Refund {refund.id} skipped due to missing Razorpay ID.")
        return redirect("payments:manage_refunds")

    logger.info(f"Processing refund for Payment ID: {payment.razorpay_payment_id}")

    try:
        # ✅ Call Razorpay API
        response = razorpay_client.payment.refund(payment.razorpay_payment_id, {
            "amount": int(payment.amount * 100),
            "speed": "normal"
        })

        logger.info(f"Razorpay Response: {response}")

        # ✅ Update DB
        payment.status = "refunded"
        payment.save()
        refund.status = "processed"
        refund.save()

        messages.success(request, "Refund approved and processed successfully.")
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay BadRequestError: {str(e)}")
        messages.error(request, f"Error processing refund: {str(e)}")
    except razorpay.errors.ServerError as e:
        logger.error(f"Razorpay ServerError: {str(e)}")
        messages.error(request, "Razorpay server error. Try again later.")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        messages.error(request, f"Error processing refund: {str(e)}")
        messages.success(request, "Refund approved and processed successfully.")

    return redirect("authentication:admin_dashboard")  # 🔥 Redirecting to dashboard

@login_required
def reject_refund(request, refund_id):
    
    if not request.user.is_staff:
        messages.error(request, "Access Denied!")
        return redirect("booking:view_bookings")

    refund = get_object_or_404(RefundRequest, id=refund_id, status="pending")
    refund.status = "rejected"
    refund.save()
    messages.warning(request, "Refund request has been rejected.")
    
    return redirect("payments:manage_refunds")

