# GrandStay Hotel Room Management System
# Booking Model & Data Access Object

import random
import string
from datetime import datetime, date
from database.db import query_all, query_one, execute, get_db

class BookingModel:
    """Handles all database operations and transactions for bookings."""

    @staticmethod
    def generate_booking_code():
        """Generate a clean, professional booking reference code."""
        today_str = datetime.now().strftime("%Y%m%d")
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"GS-{today_str}-{rand_str}"

    @staticmethod
    def get_all(search=None, status=None, date_from=None, date_to=None, limit=None, offset=None):
        """Fetch bookings with comprehensive filtering."""
        conditions = []
        params = []

        if search:
            conditions.append("""(b.booking_code LIKE %s OR 
                                  c.full_name LIKE %s OR 
                                  c.phone LIKE %s OR 
                                  r.room_number LIKE %s)""")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])

        if status and status != 'ALL':
            conditions.append("b.status = %s")
            params.append(status)

        if date_from:
            conditions.append("b.check_in >= %s")
            params.append(date_from)

        if date_to:
            conditions.append("b.check_out <= %s")
            params.append(date_to)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        limit_clause = ""
        if limit is not None:
            limit_clause = f"LIMIT {int(limit)}"
            if offset is not None:
                limit_clause += f" OFFSET {int(offset)}"

        sql = f"""
            SELECT b.*, 
                   DATEDIFF(b.check_out, b.check_in) AS total_nights,
                   c.full_name AS customer_name, c.phone AS customer_phone, c.email AS customer_email,
                   r.room_number, r.room_type,
                   p.payment_status, p.payment_method, p.id AS payment_id
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN payments p ON b.id = p.booking_id
            {where_clause}
            ORDER BY b.created_at DESC
            {limit_clause}
        """
        return query_all(sql, tuple(params))

    @staticmethod
    def get_by_id(booking_id):
        """Fetch single booking by ID with customer, room, and payment details."""
        sql = """
            SELECT b.*, 
                   DATEDIFF(b.check_out, b.check_in) AS total_nights,
                   c.full_name AS customer_name, c.phone AS customer_phone, c.email AS customer_email, c.address AS customer_address, c.id_type, c.id_number,
                   r.room_number, r.room_type, r.capacity AS room_capacity,
                   p.payment_status, p.payment_method, p.payment_date, p.id AS payment_id, p.amount AS payment_amount
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN payments p ON b.id = p.booking_id
            WHERE b.id = %s
        """
        return query_one(sql, (booking_id,))

    @staticmethod
    def get_by_code(booking_code):
        """Fetch single booking by booking reference code."""
        sql = """
            SELECT b.*, 
                   DATEDIFF(b.check_out, b.check_in) AS total_nights,
                   c.full_name AS customer_name, c.phone AS customer_phone, c.email AS customer_email,
                   r.room_number, r.room_type,
                   p.payment_status, p.payment_method, p.id AS payment_id
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN payments p ON b.id = p.booking_id
            WHERE b.booking_code = %s
        """
        return query_one(sql, (booking_code,))

    @staticmethod
    def get_recent(limit=5):
        """Fetch recent bookings for the dashboard landing page."""
        sql = """
            SELECT b.*, 
                   c.full_name AS customer_name,
                   r.room_number, r.room_type,
                   p.payment_status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN payments p ON b.id = p.booking_id
            ORDER BY b.created_at DESC
            LIMIT %s
        """
        return query_all(sql, (limit,))

    @staticmethod
    def create_booking_atomic(customer_id, room_id, check_in_str, check_out_str, guests=1, payment_method='Credit Card', initial_payment_status='Pending'):
        """
        Creates a booking with strict concurrency protection.
        Validates date ranges, checks for overlapping bookings inside a transaction,
        calculates total bill, creates booking, and initializes payment record.
        """
        try:
            check_in = datetime.strptime(str(check_in_str).split()[0], '%Y-%m-%d').date()
            check_out = datetime.strptime(str(check_out_str).split()[0], '%Y-%m-%d').date()
        except ValueError:
            return False, "Invalid date format. Please use YYYY-MM-DD.", None

        if check_out <= check_in:
            return False, "Check-out date must be at least one day after check-in date.", None

        nights = (check_out - check_in).days
        if nights < 1:
            return False, "Booking must be for at least one night.", None

        with get_db() as conn:
            with conn.cursor() as cursor:
                # 1. Fetch room details with FOR UPDATE lock to prevent race conditions
                cursor.execute("SELECT * FROM rooms WHERE id = %s FOR UPDATE", (room_id,))
                room = cursor.fetchone()
                if not room:
                    return False, "Selected room does not exist.", None

                if room['status'] == 'Maintenance':
                    return False, f"Room {room['room_number']} is currently under maintenance and cannot be booked.", None

                # 2. Check for overlapping active bookings
                cursor.execute("""
                    SELECT id, booking_code, check_in, check_out 
                    FROM bookings 
                    WHERE room_id = %s 
                      AND status IN ('CONFIRMED', 'CHECKED_IN')
                      AND check_in < %s 
                      AND check_out > %s
                    FOR UPDATE
                """, (room_id, check_out, check_in))
                overlapping = cursor.fetchone()

                if overlapping:
                    return False, f"Room {room['room_number']} is already booked from {overlapping['check_in']} to {overlapping['check_out']}.", None

                # 3. Calculate financial totals
                price_per_night = float(room['price_per_night'])
                total_amount = round(nights * price_per_night, 2)
                booking_code = BookingModel.generate_booking_code()

                # 4. Insert into bookings
                cursor.execute("""
                    INSERT INTO bookings (booking_code, customer_id, room_id, check_in, check_out, guests, price_per_night, total_amount, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'CONFIRMED')
                """, (booking_code, customer_id, room_id, check_in, check_out, guests, price_per_night, total_amount))
                booking_id = cursor.lastrowid

                # 5. Insert payment record
                pay_date = datetime.now() if initial_payment_status == 'Paid' else None
                cursor.execute("""
                    INSERT INTO payments (booking_id, amount, payment_status, payment_method, payment_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (booking_id, total_amount, initial_payment_status, payment_method, pay_date))

                # 6. Update room visual status if check-in is today
                today = date.today()
                if check_in <= today < check_out:
                    cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE id = %s AND status != 'Maintenance'", (room_id,))

        return True, "Booking confirmed successfully!", {
            'id': booking_id,
            'booking_code': booking_code,
            'total_amount': total_amount,
            'nights': nights
        }

    @staticmethod
    def cancel_booking(booking_id):
        """
        Cancel an existing booking with business rule checks.
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM bookings WHERE id = %s FOR UPDATE", (booking_id,))
                booking = cursor.fetchone()
                if not booking:
                    return False, "Booking record not found."

                if booking['status'] == 'CANCELLED':
                    return False, "This booking has already been cancelled."

                if booking['status'] == 'CHECKED_OUT':
                    return False, "Cannot cancel a booking that has already checked out."

                # Update booking status
                cursor.execute("""
                    UPDATE bookings 
                    SET status = 'CANCELLED', cancelled_at = NOW() 
                    WHERE id = %s
                """, (booking_id,))

                # Check if payment was made; if paid, set to Refunded, otherwise Pending
                cursor.execute("SELECT payment_status FROM payments WHERE booking_id = %s", (booking_id,))
                payment = cursor.fetchone()
                if payment and payment['payment_status'] == 'Paid':
                    cursor.execute("UPDATE payments SET payment_status = 'Refunded' WHERE booking_id = %s", (booking_id,))

                # Check if this room has any other active booking today
                cursor.execute("""
                    SELECT COUNT(*) AS active_count FROM bookings
                    WHERE room_id = %s 
                      AND id != %s
                      AND status IN ('CONFIRMED', 'CHECKED_IN')
                      AND check_in <= CURDATE() AND check_out > CURDATE()
                """, (booking['room_id'], booking_id))
                res = cursor.fetchone()
                if res and res['active_count'] == 0:
                    cursor.execute("""
                        UPDATE rooms 
                        SET status = 'Available' 
                        WHERE id = %s AND status = 'Occupied'
                    """, (booking['room_id'],))

        return True, "Booking cancelled successfully."

    @staticmethod
    def checkout_booking(booking_id):
        """
        Process guest check-out with validation.
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM bookings WHERE id = %s FOR UPDATE", (booking_id,))
                booking = cursor.fetchone()
                if not booking:
                    return False, "Booking record not found."

                if booking['status'] == 'CANCELLED':
                    return False, "Cannot check out a cancelled booking."

                if booking['status'] == 'CHECKED_OUT':
                    return False, "This booking has already been checked out."

                # Update status
                cursor.execute("""
                    UPDATE bookings 
                    SET status = 'CHECKED_OUT', checked_out_at = NOW() 
                    WHERE id = %s
                """, (booking_id,))

                # Re-evaluate room status
                cursor.execute("""
                    SELECT COUNT(*) AS active_count FROM bookings
                    WHERE room_id = %s 
                      AND id != %s
                      AND status IN ('CONFIRMED', 'CHECKED_IN')
                      AND check_in <= CURDATE() AND check_out > CURDATE()
                """, (booking['room_id'], booking_id))
                res = cursor.fetchone()
                if res and res['active_count'] == 0:
                    cursor.execute("""
                        UPDATE rooms 
                        SET status = 'Available' 
                        WHERE id = %s AND status = 'Occupied'
                    """, (booking['room_id'],))

        return True, "Check-out completed successfully."

    @staticmethod
    def get_dashboard_metrics():
        """Compute key summary statistics for the dashboard landing page."""
        sql = """
            SELECT
                (SELECT COUNT(*) FROM bookings) AS total_bookings,
                (SELECT COUNT(*) FROM customers) AS total_customers,
                (SELECT COUNT(*) FROM bookings WHERE check_in = CURDATE() AND status IN ('CONFIRMED', 'CHECKED_IN')) AS today_checkins,
                (SELECT COUNT(*) FROM bookings WHERE check_out = CURDATE() AND status IN ('CONFIRMED', 'CHECKED_IN')) AS today_checkouts,
                (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status = 'Paid') AS total_revenue,
                (SELECT COUNT(*) FROM bookings WHERE status = 'CANCELLED') AS total_cancellations
        """
        res = query_one(sql)
        return res or {
            'total_bookings': 0,
            'total_customers': 0,
            'today_checkins': 0,
            'today_checkouts': 0,
            'total_revenue': 0.0,
            'total_cancellations': 0
        }

    @staticmethod
    def get_monthly_revenue():
        """Fetch monthly revenue totals for the past 6-12 months for Chart.js."""
        sql = """
            SELECT 
                DATE_FORMAT(payment_date, '%b %Y') AS month_label,
                DATE_FORMAT(payment_date, '%Y-%m') AS sort_key,
                COALESCE(SUM(amount), 0) AS revenue
            FROM payments
            WHERE payment_status = 'Paid' AND payment_date IS NOT NULL
            GROUP BY sort_key, month_label
            ORDER BY sort_key ASC
            LIMIT 12
        """
        rows = query_all(sql)
        # If no paid records yet, provide current month with 0
        if not rows:
            curr_label = datetime.now().strftime("%b %Y")
            return [{'month_label': curr_label, 'revenue': 0.0}]
        return rows

    @staticmethod
    def get_booking_trends():
        """Fetch booking counts by creation month/date for Chart.js."""
        sql = """
            SELECT 
                DATE_FORMAT(created_at, '%b %Y') AS month_label,
                DATE_FORMAT(created_at, '%Y-%m') AS sort_key,
                COUNT(*) AS booking_count
            FROM bookings
            GROUP BY sort_key, month_label
            ORDER BY sort_key ASC
            LIMIT 12
        """
        rows = query_all(sql)
        if not rows:
            curr_label = datetime.now().strftime("%b %Y")
            return [{'month_label': curr_label, 'booking_count': 0}]
        return rows
