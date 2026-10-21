# GrandStay Hotel Room Management System
# Bookings Blueprint & APIs

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.booking import BookingModel
from models.customer import CustomerModel
from models.room import RoomModel
from services.booking_service import BookingService

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/bookings')
def list_bookings():
    """Active bookings management page with interactive booking wizard."""
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'ALL').strip()
    
    # Active bookings primarily shows current active reservations
    bookings = BookingModel.get_all(search=search, status=status if status != 'ALL' else None)
    customers = CustomerModel.get_all()
    rooms = RoomModel.get_all(status='Available')

    return render_template(
        'bookings.html',
        bookings=bookings,
        customers=customers,
        rooms=rooms,
        search=search,
        selected_status=status
    )

@bookings_bp.route('/booking-history')
def booking_history():
    """Historical archive of all bookings with advanced filters and invoice links."""
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'ALL').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    bookings = BookingModel.get_all(
        search=search,
        status=status if status != 'ALL' else None,
        date_from=date_from if date_from else None,
        date_to=date_to if date_to else None
    )

    return render_template(
        'booking_history.html',
        bookings=bookings,
        search=search,
        selected_status=status,
        date_from=date_from,
        date_to=date_to
    )

@bookings_bp.route('/bookings/<int:booking_id>')
def get_booking_json(booking_id):
    """API endpoint to get full details of a single booking."""
    booking = BookingModel.get_by_id(booking_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    return jsonify({'success': True, 'booking': booking})

@bookings_bp.route('/api/bookings/code/<string:booking_code>')
def get_booking_by_code_api(booking_code):
    """API endpoint to lookup booking by booking reference code."""
    booking = BookingModel.get_by_code(booking_code.strip())
    if not booking:
        return jsonify({'success': False, 'message': f'Booking with code "{booking_code}" not found.'}), 404
    return jsonify({'success': True, 'booking': booking})

@bookings_bp.route('/bookings/create', methods=['POST'])
def create_booking():
    """Create a new booking enforcing server-side concurrency and availability validation."""
    customer_id = request.form.get('customer_id')
    room_id = request.form.get('room_id')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guests = request.form.get('guests', 1)
    payment_method = request.form.get('payment_method', 'Credit Card')
    payment_status = request.form.get('payment_status', 'Pending')

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('ajax') == '1'

    if not customer_id or not room_id or not check_in or not check_out:
        msg = "Customer, Room, Check-in, and Check-out dates are all required."
        if is_ajax:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('bookings.list_bookings'))

    success, msg, booking_info = BookingService.process_new_booking(
        customer_id=customer_id,
        room_id=room_id,
        check_in_str=check_in,
        check_out_str=check_out,
        guests=guests,
        payment_method=payment_method,
        payment_status=payment_status
    )

    if success:
        if is_ajax:
            return jsonify({
                'success': True, 
                'message': msg, 
                'booking': booking_info,
                'redirect_url': url_for('billing.view_invoice', booking_id=booking_info['id'])
            })
        flash(f"{msg} Reference: {booking_info['booking_code']}", 'success')
        return redirect(url_for('bookings.list_bookings'))
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('bookings.list_bookings'))

@bookings_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking_action(booking_id):
    """Handle booking cancellation with business rules."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    success, msg = BookingService.process_cancellation(booking_id)

    if success:
        if is_ajax:
            return jsonify({'success': True, 'message': msg})
        flash(msg, 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')

    return redirect(request.referrer or url_for('bookings.list_bookings'))

@bookings_bp.route('/bookings/<int:booking_id>/checkout', methods=['POST'])
def checkout_booking_action(booking_id):
    """Handle guest check-out with business rules."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    success, msg = BookingService.process_checkout(booking_id)

    if success:
        if is_ajax:
            return jsonify({'success': True, 'message': msg})
        flash(msg, 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')

    return redirect(request.referrer or url_for('bookings.list_bookings'))
