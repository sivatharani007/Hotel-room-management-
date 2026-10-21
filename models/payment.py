# GrandStay Hotel Room Management System
# Payment & Billing Model & Data Access Object

from datetime import datetime
from database.db import query_all, query_one, execute
from config import Config

class PaymentModel:
    """Handles database queries for customer billing, payments, and invoices."""

    @staticmethod
    def get_all(search=None, status=None):
        """Fetch all billing and payment records."""
        conditions = []
        params = []

        if search:
            conditions.append("""(b.booking_code LIKE %s OR 
                                  c.full_name LIKE %s OR 
                                  r.room_number LIKE %s)""")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        if status and status != 'ALL':
            conditions.append("p.payment_status = %s")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
            SELECT p.*,
                   b.booking_code, b.check_in, b.check_out, b.price_per_night, b.total_amount, b.status AS booking_status,
                   DATEDIFF(b.check_out, b.check_in) AS total_nights,
                   c.full_name AS customer_name, c.phone AS customer_phone, c.email AS customer_email,
                   r.room_number, r.room_type
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            {where_clause}
            ORDER BY p.created_at DESC
        """
        return query_all(sql, tuple(params))

    @staticmethod
    def get_by_id(payment_id):
        """Fetch payment record by primary ID."""
        sql = "SELECT * FROM payments WHERE id = %s"
        return query_one(sql, (payment_id,))

    @staticmethod
    def get_by_booking_id(booking_id):
        """Fetch payment details for a specific booking."""
        sql = "SELECT * FROM payments WHERE booking_id = %s"
        return query_one(sql, (booking_id,))

    @staticmethod
    def mark_as_paid(payment_id, payment_method='Credit Card'):
        """Mark a bill/payment as Paid with timestamp and payment method."""
        sql = """
            UPDATE payments 
            SET payment_status = 'Paid', payment_method = %s, payment_date = NOW()
            WHERE id = %s
        """
        _, rowcount = execute(sql, (payment_method, payment_id))
        return rowcount > 0

    @staticmethod
    def mark_as_refunded(payment_id):
        """Mark a bill/payment as Refunded."""
        sql = "UPDATE payments SET payment_status = 'Refunded' WHERE id = %s"
        _, rowcount = execute(sql, (payment_id,))
        return rowcount > 0

    @staticmethod
    def get_invoice_details(booking_id):
        """
        Fetch complete invoice data with breakdown of nights, room rates,
        tax calculation, customer profile, and payment history.
        """
        sql = """
            SELECT b.*,
                   DATEDIFF(b.check_out, b.check_in) AS total_nights,
                   c.full_name AS customer_name, c.phone AS customer_phone, c.email AS customer_email, 
                   c.address AS customer_address, c.id_type, c.id_number,
                   r.room_number, r.room_type, r.capacity,
                   p.id AS payment_id, p.payment_status, p.payment_method, p.payment_date, p.amount AS billed_amount
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN payments p ON b.id = p.booking_id
            WHERE b.id = %s
        """
        invoice = query_one(sql, (booking_id,))
        if not invoice:
            return None

        # Add computed tax and totals
        subtotal = float(invoice['total_amount'])
        tax_rate = Config.HOTEL_TAX_RATE
        tax_amount = round(subtotal * tax_rate, 2)
        grand_total = round(subtotal + tax_amount, 2)

        invoice['subtotal'] = subtotal
        invoice['tax_rate_percent'] = int(tax_rate * 100)
        invoice['tax_amount'] = tax_amount
        invoice['grand_total'] = grand_total
        invoice['currency'] = Config.HOTEL_CURRENCY
        invoice['hotel_name'] = Config.HOTEL_NAME
        invoice['hotel_tagline'] = Config.HOTEL_TAGLINE
        invoice['hotel_phone'] = Config.HOTEL_PHONE
        invoice['hotel_email'] = Config.HOTEL_EMAIL
        invoice['hotel_address'] = Config.HOTEL_ADDRESS
        invoice['invoice_date'] = datetime.now().strftime("%B %d, %Y")

        return invoice
