# GrandStay Hotel Room Management System
# Customer Model & Data Access Object

from database.db import query_all, query_one, execute, get_db

class CustomerModel:
    """Handles all database operations related to customers."""

    @staticmethod
    def get_all(search=None):
        """Fetch all customers with optional search filtering."""
        if search:
            sql = """
                SELECT c.*, 
                       (SELECT COUNT(*) FROM bookings b WHERE b.customer_id = c.id) AS total_bookings
                FROM customers c
                WHERE c.full_name LIKE %s OR c.phone LIKE %s OR c.email LIKE %s OR c.id = %s
                ORDER BY c.created_at DESC
            """
            search_param = f"%{search}%"
            # Attempt integer parse for ID search
            try:
                id_search = int(search)
            except ValueError:
                id_search = -1
            return query_all(sql, (search_param, search_param, search_param, id_search))
        else:
            sql = """
                SELECT c.*, 
                       (SELECT COUNT(*) FROM bookings b WHERE b.customer_id = c.id) AS total_bookings
                FROM customers c
                ORDER BY c.created_at DESC
            """
            return query_all(sql)

    @staticmethod
    def get_by_id(customer_id):
        """Fetch a single customer by primary ID."""
        sql = "SELECT * FROM customers WHERE id = %s"
        return query_one(sql, (customer_id,))

    @staticmethod
    def find_duplicate(email, phone, exclude_id=None):
        """Check if email or phone is already registered by another customer."""
        if exclude_id:
            sql = "SELECT * FROM customers WHERE (email = %s OR phone = %s) AND id != %s LIMIT 1"
            return query_one(sql, (email, phone, exclude_id))
        else:
            sql = "SELECT * FROM customers WHERE email = %s OR phone = %s LIMIT 1"
            return query_one(sql, (email, phone))

    @staticmethod
    def create(full_name, phone, email, address="", id_type="National ID", id_number=""):
        """Register a new customer."""
        sql = """
            INSERT INTO customers (full_name, phone, email, address, id_type, id_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        last_id, _ = execute(sql, (full_name, phone, email, address, id_type, id_number))
        return last_id

    @staticmethod
    def update(customer_id, full_name, phone, email, address="", id_type="National ID", id_number=""):
        """Update existing customer details."""
        sql = """
            UPDATE customers 
            SET full_name = %s, phone = %s, email = %s, address = %s, id_type = %s, id_number = %s
            WHERE id = %s
        """
        _, rowcount = execute(sql, (full_name, phone, email, address, id_type, id_number, customer_id))
        return rowcount > 0

    @staticmethod
    def delete(customer_id):
        """
        Delete a customer only if they have no associated bookings.
        Returns (success: bool, message: str)
        """
        # Check for existing bookings
        check_sql = "SELECT COUNT(*) AS booking_count FROM bookings WHERE customer_id = %s"
        res = query_one(check_sql, (customer_id,))
        if res and res.get('booking_count', 0) > 0:
            return False, f"Cannot delete customer: {res['booking_count']} booking record(s) exist for this customer."

        sql = "DELETE FROM customers WHERE id = %s"
        _, rowcount = execute(sql, (customer_id,))
        if rowcount > 0:
            return True, "Customer deleted successfully."
        return False, "Customer not found."

    @staticmethod
    def get_booking_history(customer_id):
        """Fetch all historical bookings for a given customer."""
        sql = """
            SELECT b.*, r.room_number, r.room_type, p.payment_status
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            LEFT JOIN payments p ON b.id = p.booking_id
            WHERE b.customer_id = %s
            ORDER BY b.check_in DESC
        """
        return query_all(sql, (customer_id,))

    @staticmethod
    def count_all():
        """Count total registered customers."""
        res = query_one("SELECT COUNT(*) AS total FROM customers")
        return res['total'] if res else 0
