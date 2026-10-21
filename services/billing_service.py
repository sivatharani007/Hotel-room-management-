# GrandStay Hotel Room Management System
# Billing Service - Calculation & Invoicing Layer

from models.payment import PaymentModel
from config import Config

class BillingService:
    """Handles financial computations, invoice generation, and payment lifecycle."""

    @staticmethod
    def calculate_bill(nights, price_per_night, tax_rate=None):
        """
        Calculates subtotal, tax amount, and final total.
        """
        if tax_rate is None:
            tax_rate = Config.HOTEL_TAX_RATE

        subtotal = round(float(nights) * float(price_per_night), 2)
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)

        return {
            'nights': nights,
            'price_per_night': float(price_per_night),
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax,
            'total': total
        }

    @staticmethod
    def process_payment(payment_id, payment_method='Credit Card'):
        """Mark a bill as paid with recorded timestamp."""
        payment = PaymentModel.get_by_id(payment_id)
        if not payment:
            return False, "Payment record not found."
            
        if payment['payment_status'] == 'Paid':
            return False, "This bill has already been marked as Paid."

        success = PaymentModel.mark_as_paid(payment_id, payment_method)
        if success:
            return True, f"Payment marked as Paid successfully via {payment_method}."
        return False, "Failed to update payment record."

    @staticmethod
    def process_refund(payment_id):
        """Mark a bill as refunded."""
        payment = PaymentModel.get_by_id(payment_id)
        if not payment:
            return False, "Payment record not found."

        success = PaymentModel.mark_as_refunded(payment_id)
        if success:
            return True, "Payment status updated to Refunded."
        return False, "Failed to update payment status."

    @staticmethod
    def get_invoice(booking_id):
        """Retrieve complete formatted invoice data."""
        return PaymentModel.get_invoice_details(booking_id)
