# GrandStay Hotel Room Management System
# Main Flask Application Entry Point

import os
from datetime import datetime, date
from flask import Flask, render_template
from config import Config
from database.db import test_connection

# Import Blueprints
from routes import (
    dashboard_bp,
    rooms_bp,
    customers_bp,
    bookings_bp,
    billing_bp,
    reports_bp,
    general_bp
)

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(general_bp)

    # Global Context Processors (available in all Jinja templates)
    @app.context_processor
    def inject_global_data():
        return {
            'hotel_name': Config.HOTEL_NAME,
            'hotel_tagline': Config.HOTEL_TAGLINE,
            'hotel_phone': Config.HOTEL_PHONE,
            'hotel_email': Config.HOTEL_EMAIL,
            'currency': Config.HOTEL_CURRENCY,
            'current_date_str': datetime.now().strftime("%A, %B %d, %Y"),
            'current_year': datetime.now().year
        }

    # Custom Jinja Template Filters
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format number as currency: $1,250.00"""
        try:
            val = float(amount or 0)
            return f"{Config.HOTEL_CURRENCY}{val:,.2f}"
        except (ValueError, TypeError):
            return f"{Config.HOTEL_CURRENCY}0.00"

    @app.template_filter('format_date')
    def date_filter(val, fmt="%b %d, %Y"):
        """Format date/datetime objects or strings to readable format."""
        if not val:
            return "N/A"
        if isinstance(val, (datetime, date)):
            return val.strftime(fmt)
        try:
            d = datetime.strptime(str(val).split()[0], "%Y-%m-%d")
            return d.strftime(fmt)
        except Exception:
            return str(val)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('404.html', error_title="500 - Internal Server Error", error_msg="Something unexpected happened on the server. Please check your MySQL database connection or terminal logs."), 500

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 65)
    print(f"🏨 {Config.HOTEL_NAME}")
    print(f"   {Config.HOTEL_TAGLINE}")
    print("=" * 65)
    
    # Pre-flight MySQL connection test
    is_connected, db_msg = test_connection()
    if is_connected:
        print("✅ [Database] MySQL connection established successfully.")
    else:
        print(f"⚠️  [Database Warning] {db_msg}")
        print("💡 [Tip] Start MySQL in XAMPP or Windows Services, then import database/schema.sql.")

    print(f"🚀 Server running on: http://127.0.0.1:5000")
    print("👉 Press Ctrl+C in terminal to stop.")
    print("=" * 65)
    
    app.run(host='127.0.0.1', port=5000, debug=Config.DEBUG)
