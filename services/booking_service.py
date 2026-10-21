# GrandStay Hotel Room Management System
# Booking Service - Business Logic Layer

from datetime import datetime
from models.booking import BookingModel
from models.room import RoomModel
from models.customer import CustomerModel

class BookingService:
    """Encapsulates business rules, validation, and workflow orchestration for bookings."""

    @staticmethod
    def validate_dates(check_in_str, check_out_str):
        """
        Validates check-in and check-out dates.
        Returns (is_valid: bool, error_msg: str or None, check_in_date, check_out_date, nights: int)
        """
        if not check_in_str or not check_out_str:
            return False, "Both check-in and check-out dates are required.", None, None, 0

        try:
            check_in = datetime.strptime(str(check_in_str).split()[0], '%Y-%m-%d').date()
            check_out = datetime.strptime(str(check_out_str).split()[0], '%Y-%m-%d').date()
        except ValueError:
            return False, "Dates must follow the YYYY-MM-DD format.", None, None, 0

        if check_out <= check_in:
            return False, "Check-out date must be later than check-in date.", None, None, 0

        nights = (check_out - check_in).days
        if nights < 1:
            return False, "Minimum stay is 1 night.", None, None, 0

        return True, None, check_in, check_out, nights

    @staticmethod
    def search_available_rooms(check_in_str, check_out_str, room_type=None, guests=1):
        """
        Validate dates and query rooms that are not in maintenance and not booked.
        """
        valid, err, check_in, check_out, nights = BookingService.validate_dates(check_in_str, check_out_str)
        if not valid:
            return False, err, []

        rooms = RoomModel.get_available_rooms(
            check_in=check_in, 
            check_out=check_out, 
            room_type=room_type, 
            min_capacity=guests
        )
        return True, f"Found {len(rooms)} available room(s).", rooms

    @staticmethod
    def process_new_booking(customer_id, room_id, check_in_str, check_out_str, guests=1, payment_method='Credit Card', payment_status='Pending'):
        """
        Full booking processing with validation, capacity checks, and concurrency safety.
        """
        valid, err, check_in, check_out, nights = BookingService.validate_dates(check_in_str, check_out_str)
        if not valid:
            return False, err, None

        # Verify customer exists
        customer = CustomerModel.get_by_id(customer_id)
        if not customer:
            return False, "Selected customer does not exist in records.", None

        # Verify room capacity
        room = RoomModel.get_by_id(room_id)
        if not room:
            return False, "Selected room does not exist.", None

        try:
            guests_num = int(guests)
        except (ValueError, TypeError):
            guests_num = 1

        if guests_num > room['capacity']:
            return False, f"Room {room['room_number']} capacity is {room['capacity']} guests, but {guests_num} requested.", None

        # Execute atomic booking creation in database
        success, msg, booking_info = BookingModel.create_booking_atomic(
            customer_id=customer_id,
            room_id=room_id,
            check_in_str=check_in,
            check_out_str=check_out,
            guests=guests_num,
            payment_method=payment_method,
            initial_payment_status=payment_status
        )
        return success, msg, booking_info

    @staticmethod
    def process_cancellation(booking_id):
        """Process cancellation with validation."""
        booking = BookingModel.get_by_id(booking_id)
        if not booking:
            return False, "Booking not found."
            
        if booking['status'] == 'CHECKED_OUT':
            return False, "Completed bookings (Checked-Out) cannot be cancelled."

        if booking['status'] == 'CANCELLED':
            return False, "This booking has already been cancelled."

        return BookingModel.cancel_booking(booking_id)

    @staticmethod
    def process_checkout(booking_id):
        """Process check-out with validation."""
        booking = BookingModel.get_by_id(booking_id)
        if not booking:
            return False, "Booking not found."

        if booking['status'] == 'CANCELLED':
            return False, "Cannot check out a cancelled booking."

        if booking['status'] == 'CHECKED_OUT':
            return False, "Guest has already checked out."

        return BookingModel.checkout_booking(booking_id)
