# GrandStay Hotel Room Management System
# Reports & Analytics Blueprint

import io
import csv
from flask import Blueprint, render_template, request, Response, jsonify
from models.room import RoomModel
from models.booking import BookingModel
from database.db import query_all, query_one

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
def reports_view():
    """Render comprehensive reports and analytics page."""
    # Summary metrics
    room_stats = RoomModel.get_statistics()
    booking_metrics = BookingModel.get_dashboard_metrics()

    total_rooms = room_stats['total_rooms']
    occupied_rooms = room_stats['occupied_rooms']
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0.0

    # Most booked room types
    sql_popular_types = """
        SELECT r.room_type, COUNT(b.id) AS total_booked, COALESCE(SUM(b.total_amount), 0) AS revenue_generated
        FROM rooms r
        LEFT JOIN bookings b ON r.id = b.room_id
        GROUP BY r.room_type
        ORDER BY total_booked DESC
    """
    popular_types = query_all(sql_popular_types)

    # Booking status breakdown
    sql_status_breakdown = """
        SELECT status, COUNT(*) AS count
        FROM bookings
        GROUP BY status
    """
    status_breakdown = query_all(sql_status_breakdown)

    return render_template(
        'reports.html',
        room_stats=room_stats,
        booking_metrics=booking_metrics,
        occupancy_rate=occupancy_rate,
        popular_types=popular_types,
        status_breakdown=status_breakdown
    )

@reports_bp.route('/api/charts')
def reports_charts_api():
    """API endpoint providing comprehensive analytics data for Chart.js on the reports page."""
    monthly_rev = BookingModel.get_monthly_revenue()
    booking_trends = BookingModel.get_booking_trends()
    room_stats = RoomModel.get_statistics()
    
    sql_popular = """
        SELECT r.room_type, COUNT(b.id) AS total_booked
        FROM rooms r
        LEFT JOIN bookings b ON r.id = b.room_id
        GROUP BY r.room_type
    """
    popular_types = query_all(sql_popular)

    return jsonify({
        'success': True,
        'revenue': {
            'labels': [row['month_label'] for row in monthly_rev],
            'data': [float(row['revenue']) for row in monthly_rev]
        },
        'trends': {
            'labels': [row['month_label'] for row in booking_trends],
            'data': [int(row['booking_count']) for row in booking_trends]
        },
        'popular_types': {
            'labels': [row['room_type'] for row in popular_types],
            'data': [int(row['total_booked']) for row in popular_types]
        },
        'room_status': {
            'labels': ['Available', 'Occupied', 'Maintenance'],
            'data': [
                room_stats['available_rooms'],
                room_stats['occupied_rooms'],
                room_stats['maintenance_rooms']
            ]
        }
    })

@reports_bp.route('/export/bookings')
def export_bookings_csv():
    """Export all booking records to a CSV file."""
    bookings = BookingModel.get_all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Booking Code', 'Customer Name', 'Customer Phone', 'Customer Email',
        'Room Number', 'Room Type', 'Check-In Date', 'Check-Out Date',
        'Nights', 'Price Per Night', 'Total Amount', 'Booking Status',
        'Payment Status', 'Created At'
    ])

    for b in bookings:
        writer.writerow([
            b.get('booking_code', ''),
            b.get('customer_name', ''),
            b.get('customer_phone', ''),
            b.get('customer_email', ''),
            b.get('room_number', ''),
            b.get('room_type', ''),
            b.get('check_in', ''),
            b.get('check_out', ''),
            b.get('total_nights', ''),
            b.get('price_per_night', ''),
            b.get('total_amount', ''),
            b.get('status', ''),
            b.get('payment_status', 'Pending'),
            b.get('created_at', '')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=grandstay_bookings_report.csv"}
    )

@reports_bp.route('/export/rooms')
def export_rooms_csv():
    """Export room inventory status to a CSV file."""
    rooms = RoomModel.get_all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Room ID', 'Room Number', 'Room Type', 'Price Per Night',
        'Capacity', 'Current Status', 'Description'
    ])

    for r in rooms:
        writer.writerow([
            r.get('id', ''),
            r.get('room_number', ''),
            r.get('room_type', ''),
            r.get('price_per_night', ''),
            r.get('capacity', ''),
            r.get('status', ''),
            r.get('description', '')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=grandstay_rooms_inventory.csv"}
    )
