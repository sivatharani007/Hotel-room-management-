# GrandStay Hotel Room Management System
# Customers Blueprint & APIs

import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.customer import CustomerModel

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PHONE_REGEX = r'^\+?[0-9\s\-\(\)]{7,20}$'

@customers_bp.route('/')
def list_customers():
    """Display customers list with search and summary counters."""
    search = request.args.get('search', '').strip()
    customers = CustomerModel.get_all(search=search)
    total_count = CustomerModel.count_all()

    return render_template(
        'customers.html',
        customers=customers,
        total_count=total_count,
        search=search
    )

@customers_bp.route('/<int:customer_id>')
def get_customer_json(customer_id):
    """API endpoint to get customer details as JSON."""
    customer = CustomerModel.get_by_id(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    return jsonify({'success': True, 'customer': customer})

@customers_bp.route('/<int:customer_id>/history')
def get_customer_history(customer_id):
    """API endpoint to fetch all booking history for a specific customer."""
    customer = CustomerModel.get_by_id(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
        
    history = CustomerModel.get_booking_history(customer_id)
    return jsonify({
        'success': True,
        'customer': customer,
        'bookings': history
    })

@customers_bp.route('/api/search')
def search_customers_api():
    """API search endpoint for booking wizard customer auto-suggest."""
    q = request.args.get('q', '').strip()
    customers = CustomerModel.get_all(search=q)
    return jsonify({'success': True, 'customers': customers})

@customers_bp.route('/add', methods=['POST'])
def add_customer():
    """Register a new customer with validation and duplicate prevention."""
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    id_type = request.form.get('id_type', 'Passport / National ID').strip()
    id_number = request.form.get('id_number', '').strip()
    return_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.form.get('ajax') == '1'

    # Validation
    if not full_name or not phone or not email:
        msg = 'Full Name, Phone Number, and Email Address are required fields.'
        if return_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('customers.list_customers'))

    if not re.match(EMAIL_REGEX, email):
        msg = 'Please enter a valid email address (e.g., name@example.com).'
        if return_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('customers.list_customers'))

    if not re.match(PHONE_REGEX, phone):
        msg = 'Please enter a valid telephone/mobile number.'
        if return_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('customers.list_customers'))

    # Duplicate check
    duplicate = CustomerModel.find_duplicate(email, phone)
    if duplicate:
        msg = f'A customer with email ({email}) or phone ({phone}) already exists (ID: #{duplicate["id"]} - {duplicate["full_name"]}).'
        if return_json:
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('customers.list_customers'))

    new_id = CustomerModel.create(full_name, phone, email, address, id_type, id_number)
    success_msg = f'Customer "{full_name}" registered successfully!'

    if return_json:
        return jsonify({
            'success': True, 
            'message': success_msg,
            'customer': {
                'id': new_id,
                'full_name': full_name,
                'phone': phone,
                'email': email
            }
        })

    flash(success_msg, 'success')
    return redirect(url_for('customers.list_customers'))

@customers_bp.route('/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    """Update existing customer details."""
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    id_type = request.form.get('id_type', 'Passport / National ID').strip()
    id_number = request.form.get('id_number', '').strip()

    if not full_name or not phone or not email:
        flash('Full Name, Phone Number, and Email Address are required.', 'error')
        return redirect(url_for('customers.list_customers'))

    if not re.match(EMAIL_REGEX, email):
        flash('Invalid email address format.', 'error')
        return redirect(url_for('customers.list_customers'))

    # Check duplicates excluding current ID
    duplicate = CustomerModel.find_duplicate(email, phone, exclude_id=customer_id)
    if duplicate:
        flash(f'Another customer is already registered with this email or phone.', 'error')
        return redirect(url_for('customers.list_customers'))

    CustomerModel.update(customer_id, full_name, phone, email, address, id_type, id_number)
    flash(f'Customer "{full_name}" profile updated successfully!', 'success')
    return redirect(url_for('customers.list_customers'))

@customers_bp.route('/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    """Safely delete customer if no booking history exists."""
    success, message = CustomerModel.delete(customer_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('customers.list_customers'))
