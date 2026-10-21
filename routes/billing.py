# GrandStay Hotel Room Management System
# Billing & Invoices Blueprint

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.payment import PaymentModel
from models.room import RoomModel
from services.billing_service import BillingService
from services.booking_service import BookingService

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/billing')
def list_billing():
    """Display billing overview and payment records."""
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'ALL').strip()

    payments = PaymentModel.get_all(search=search, status=status)

    # Summary metrics for billing
    total_billed = sum(float(p['amount']) for p in payments)
    total_paid = sum(float(p['amount']) for p in payments if p['payment_status'] == 'Paid')
    total_pending = sum(float(p['amount']) for p in payments if p['payment_status'] == 'Pending')

    return render_template(
        'billing.html',
        payments=payments,
        search=search,
        selected_status=status,
        total_billed=total_billed,
        total_paid=total_paid,
        total_pending=total_pending
    )

@billing_bp.route('/billing/<int:payment_id>/pay', methods=['POST'])
def mark_paid_action(payment_id):
    """Record receipt of payment."""
    payment_method = request.form.get('payment_method', 'Credit Card').strip()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    success, msg = BillingService.process_payment(payment_id, payment_method)
    if success:
        if is_ajax:
            return jsonify({'success': True, 'message': msg})
        flash(msg, 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')

    return redirect(request.referrer or url_for('billing.list_billing'))

@billing_bp.route('/invoice/<int:booking_id>')
def view_invoice(booking_id):
    """Render professional printable invoice layout."""
    invoice = BillingService.get_invoice(booking_id)
    if not invoice:
        flash("Invoice not found for this booking reference.", "error")
        return redirect(url_for('billing.list_billing'))

    return render_template('invoice.html', invoice=invoice)

@billing_bp.route('/api/billing/estimate')
def calculate_estimate_api():
    """Calculate nights, price per night, and total bill dynamically for frontend forms."""
    check_in_str = request.args.get('check_in', '')
    check_out_str = request.args.get('check_out', '')
    room_id = request.args.get('room_id', '')

    valid, err, check_in, check_out, nights = BookingService.validate_dates(check_in_str, check_out_str)
    if not valid:
        return jsonify({'success': False, 'message': err}), 400

    if not room_id:
        return jsonify({'success': False, 'message': 'Room ID required'}), 400

    room = RoomModel.get_by_id(room_id)
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404

    price_per_night = float(room['price_per_night'])
    breakdown = BillingService.calculate_bill(nights, price_per_night)

    return jsonify({
        'success': True,
        'room_number': room['room_number'],
        'room_type': room['room_type'],
        'price_per_night': price_per_night,
        'nights': nights,
        'subtotal': breakdown['subtotal'],
        'tax_amount': breakdown['tax_amount'],
        'total': breakdown['total']
    })
