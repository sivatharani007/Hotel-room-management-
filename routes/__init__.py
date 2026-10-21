# Routes package initializer
from .dashboard import dashboard_bp
from .rooms import rooms_bp
from .customers import customers_bp
from .bookings import bookings_bp
from .billing import billing_bp
from .reports import reports_bp
from .general import general_bp

__all__ = [
    'dashboard_bp',
    'rooms_bp',
    'customers_bp',
    'bookings_bp',
    'billing_bp',
    'reports_bp',
    'general_bp'
]
