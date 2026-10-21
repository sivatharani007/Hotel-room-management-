# GrandStay Hotel Room Management System
# General Blueprint - About Project & Settings

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from database.db import test_connection, init_db

general_bp = Blueprint('general', __name__)

@general_bp.route('/about')
def about_project():
    """Render About Project presentation page for college mini-project demonstration."""
    return render_template('about.html')

@general_bp.route('/settings')
def settings_view():
    """Render settings and system configuration page."""
    is_connected, db_msg = test_connection()
    return render_template(
        'settings.html',
        config=Config,
        db_connected=is_connected,
        db_message=db_msg
    )

@general_bp.route('/settings/test-db')
def test_db_api():
    """Test MySQL connection on demand."""
    is_connected, msg = test_connection()
    return jsonify({
        'connected': is_connected,
        'message': msg
    })

@general_bp.route('/settings/init-db', methods=['POST'])
def initialize_database_action():
    """Initialize database and seed sample data directly from the interface."""
    success, msg = init_db()
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('general.settings_view'))
