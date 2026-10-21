# GrandStay Hotel Room Management System
# Dashboard Blueprint & APIs

from flask import Blueprint, render_template, jsonify
from models.room import RoomModel
from models.booking import BookingModel
from database.db import test_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def dashboard_view():
    """Render main dashboard landing page."""
    # Check DB connection status
    is_connected, db_msg = test_connection()
    
    if not is_connected:
        return render_template(
            'dashboard.html',
            db_connected=False,
            db_error=db_msg,
            stats={},
            recent_bookings=[]
        )

    # Sync daily room status
    try:
        RoomModel.sync_daily_occupancy()
    except Exception:
        pass

    room_stats = RoomModel.get_statistics()
    booking_metrics = BookingModel.get_dashboard_metrics()
    recent_bookings = BookingModel.get_recent(limit=6)

    # Combined stats dictionary
    stats = {
        'total_rooms': room_stats['total_rooms'],
        'available_rooms': room_stats['available_rooms'],
        'occupied_rooms': room_stats['occupied_rooms'],
        'maintenance_rooms': room_stats['maintenance_rooms'],
        'total_bookings': booking_metrics['total_bookings'],
        'total_customers': booking_metrics['total_customers'],
        'today_checkins': booking_metrics['today_checkins'],
        'today_checkouts': booking_metrics['today_checkouts'],
        'total_revenue': float(booking_metrics['total_revenue']),
        'total_cancellations': booking_metrics['total_cancellations']
    }

    return render_template(
        'dashboard.html',
        db_connected=True,
        stats=stats,
        recent_bookings=recent_bookings
    )

@dashboard_bp.route('/api/dashboard/charts')
def dashboard_charts_api():
    """API endpoint providing structured dataset for Chart.js dashboard charts."""
    try:
        room_stats = RoomModel.get_statistics()
        room_types = RoomModel.get_room_types_distribution()
        monthly_rev = BookingModel.get_monthly_revenue()
        booking_trends = BookingModel.get_booking_trends()

        # 1. Occupancy Doughnut Chart
        occupancy_data = {
            'labels': ['Available', 'Occupied', 'Maintenance'],
            'data': [
                room_stats['available_rooms'],
                room_stats['occupied_rooms'],
                room_stats['maintenance_rooms']
            ]
        }

        # 2. Room Type Distribution Pie/Polar Chart
        room_type_data = {
            'labels': [row['room_type'] for row in room_types],
            'data': [row['count'] for row in room_types]
        }

        # 3. Monthly Revenue Bar/Line Chart
        revenue_data = {
            'labels': [row['month_label'] for row in monthly_rev],
            'data': [float(row['revenue']) for row in monthly_rev]
        }

        # 4. Booking Trends Line Chart
        trends_data = {
            'labels': [row['month_label'] for row in booking_trends],
            'data': [int(row['booking_count']) for row in booking_trends]
        }

        return jsonify({
            'success': True,
            'occupancy': occupancy_data,
            'room_types': room_type_data,
            'revenue': revenue_data,
            'trends': trends_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
