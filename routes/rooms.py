# GrandStay Hotel Room Management System
# Rooms Blueprint & APIs

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.room import RoomModel

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@rooms_bp.route('/')
def list_rooms():
    """Display rooms page with search, filters, and cards/table toggle."""
    search = request.args.get('search', '').strip()
    room_type = request.args.get('room_type', 'ALL').strip()
    status = request.args.get('status', 'ALL').strip()
    sort_by = request.args.get('sort_by', 'room_number_asc').strip()

    rooms = RoomModel.get_all(search=search, room_type=room_type, status=status, sort_by=sort_by)
    stats = RoomModel.get_statistics()

    return render_template(
        'rooms.html',
        rooms=rooms,
        stats=stats,
        search=search,
        selected_type=room_type,
        selected_status=status,
        selected_sort=sort_by
    )

@rooms_bp.route('/<int:room_id>')
def get_room_json(room_id):
    """API endpoint to get room details as JSON for modal viewer/editor."""
    room = RoomModel.get_by_id(room_id)
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404
    return jsonify({'success': True, 'room': room})

@rooms_bp.route('/add', methods=['POST'])
def add_room():
    """Add a new room with input validation."""
    room_number = request.form.get('room_number', '').strip()
    room_type = request.form.get('room_type', '').strip()
    price_per_night = request.form.get('price_per_night', '').strip()
    capacity = request.form.get('capacity', '2').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'Available').strip()

    # Validations
    if not room_number or not room_type or not price_per_night:
        flash('Room Number, Room Type, and Price Per Night are required fields.', 'error')
        return redirect(url_for('rooms.list_rooms'))

    try:
        price = float(price_per_night)
        if price <= 0:
            flash('Price per night must be greater than zero.', 'error')
            return redirect(url_for('rooms.list_rooms'))
    except ValueError:
        flash('Invalid price value provided.', 'error')
        return redirect(url_for('rooms.list_rooms'))

    try:
        cap = int(capacity)
        if cap < 1:
            flash('Capacity must be at least 1 guest.', 'error')
            return redirect(url_for('rooms.list_rooms'))
    except ValueError:
        cap = 2

    # Check for duplicate room number
    existing = RoomModel.get_by_number(room_number)
    if existing:
        flash(f'Room Number "{room_number}" already exists. Please choose a unique room number.', 'error')
        return redirect(url_for('rooms.list_rooms'))

    RoomModel.create(room_number, room_type, price, cap, description, status)
    flash(f'Room {room_number} ({room_type}) added successfully!', 'success')
    return redirect(url_for('rooms.list_rooms'))

@rooms_bp.route('/edit/<int:room_id>', methods=['POST'])
def edit_room(room_id):
    """Update room details."""
    room_number = request.form.get('room_number', '').strip()
    room_type = request.form.get('room_type', '').strip()
    price_per_night = request.form.get('price_per_night', '').strip()
    capacity = request.form.get('capacity', '2').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'Available').strip()

    if not room_number or not room_type or not price_per_night:
        flash('Please fill in all required room details.', 'error')
        return redirect(url_for('rooms.list_rooms'))

    try:
        price = float(price_per_night)
        cap = int(capacity)
    except ValueError:
        flash('Invalid numeric format for price or capacity.', 'error')
        return redirect(url_for('rooms.list_rooms'))

    # Check for duplicate room number excluding current room
    existing = RoomModel.get_by_number(room_number, exclude_id=room_id)
    if existing:
        flash(f'Another room already has the number "{room_number}".', 'error')
        return redirect(url_for('rooms.list_rooms'))

    RoomModel.update(room_id, room_number, room_type, price, cap, description, status)
    flash(f'Room {room_number} updated successfully!', 'success')
    return redirect(url_for('rooms.list_rooms'))

@rooms_bp.route('/delete/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    """Safely delete room checking for bookings first."""
    success, message = RoomModel.delete(room_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('rooms.list_rooms'))

@rooms_bp.route('/api/available')
def get_available_rooms_api():
    """
    API endpoint for dynamic room lookup in the booking wizard.
    Query params: check_in, check_out, room_type, guests
    """
    check_in = request.args.get('check_in', '').strip()
    check_out = request.args.get('check_out', '').strip()
    room_type = request.args.get('room_type', 'ALL').strip()
    guests = request.args.get('guests', 1)

    if not check_in or not check_out:
        return jsonify({'success': False, 'message': 'Both check_in and check_out are required.'}), 400

    rooms = RoomModel.get_available_rooms(check_in, check_out, room_type, guests)
    return jsonify({
        'success': True,
        'count': len(rooms),
        'rooms': rooms
    })
