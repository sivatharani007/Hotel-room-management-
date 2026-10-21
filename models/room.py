# GrandStay Hotel Room Management System
# Room Model & Data Access Object

from database.db import query_all, query_one, execute, get_db

class RoomModel:
    """Handles all database operations related to hotel rooms."""

    @staticmethod
    def get_all(search=None, room_type=None, status=None, sort_by='room_number_asc'):
        """
        Fetch all rooms with dynamic search, filter, and sort options.
        """
        conditions = []
        params = []

        if search:
            conditions.append("(room_number LIKE %s OR description LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        if room_type and room_type != 'ALL':
            conditions.append("room_type = %s")
            params.append(room_type)

        if status and status != 'ALL':
            conditions.append("status = %s")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Sorting logic
        sort_map = {
            'room_number_asc': "CAST(room_number AS UNSIGNED) ASC, room_number ASC",
            'price_asc': "price_per_night ASC",
            'price_desc': "price_per_night DESC",
            'capacity_desc': "capacity DESC",
            'status_asc': "status ASC"
        }
        order_clause = sort_map.get(sort_by, "CAST(room_number AS UNSIGNED) ASC")

        sql = f"""
            SELECT r.*,
                   (SELECT COUNT(*) FROM bookings b 
                    WHERE b.room_id = r.id AND b.status IN ('CONFIRMED', 'CHECKED_IN')) AS active_bookings_count
            FROM rooms r
            {where_clause}
            ORDER BY {order_clause}
        """
        return query_all(sql, tuple(params))

    @staticmethod
    def get_by_id(room_id):
        """Fetch a single room by its ID."""
        sql = "SELECT * FROM rooms WHERE id = %s"
        return query_one(sql, (room_id,))

    @staticmethod
    def get_by_number(room_number, exclude_id=None):
        """Find room by room number to prevent duplicates."""
        if exclude_id:
            sql = "SELECT * FROM rooms WHERE room_number = %s AND id != %s"
            return query_one(sql, (room_number, exclude_id))
        else:
            sql = "SELECT * FROM rooms WHERE room_number = %s"
            return query_one(sql, (room_number,))

    @staticmethod
    def create(room_number, room_type, price_per_night, capacity, description, status='Available'):
        """Add a new room to the database."""
        sql = """
            INSERT INTO rooms (room_number, room_type, price_per_night, capacity, description, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        last_id, _ = execute(sql, (room_number, room_type, price_per_night, capacity, description, status))
        return last_id

    @staticmethod
    def update(room_id, room_number, room_type, price_per_night, capacity, description, status):
        """Update room details."""
        sql = """
            UPDATE rooms
            SET room_number = %s, room_type = %s, price_per_night = %s, 
                capacity = %s, description = %s, status = %s
            WHERE id = %s
        """
        _, rowcount = execute(sql, (room_number, room_type, price_per_night, capacity, description, status, room_id))
        return rowcount > 0

    @staticmethod
    def delete(room_id):
        """
        Delete a room only if it has no associated booking records.
        Returns (success: bool, message: str)
        """
        check_sql = "SELECT COUNT(*) AS booking_count FROM bookings WHERE room_id = %s"
        res = query_one(check_sql, (room_id,))
        if res and res.get('booking_count', 0) > 0:
            return False, f"Cannot delete room: {res['booking_count']} booking record(s) are linked to this room. Consider changing status to 'Maintenance' instead."

        sql = "DELETE FROM rooms WHERE id = %s"
        _, rowcount = execute(sql, (room_id,))
        if rowcount > 0:
            return True, "Room deleted successfully."
        return False, "Room not found."

    @staticmethod
    def get_available_rooms(check_in, check_out, room_type=None, min_capacity=None):
        """
        Find rooms available for the entire requested date range.
        Excludes rooms currently marked Maintenance.
        Excludes rooms with active overlapping bookings.
        """
        conditions = [
            "r.status != 'Maintenance'",
            """r.id NOT IN (
                SELECT b.room_id FROM bookings b
                WHERE b.status IN ('CONFIRMED', 'CHECKED_IN')
                  AND b.check_in < %s
                  AND b.check_out > %s
            )"""
        ]
        params = [check_out, check_in]

        if room_type and room_type != 'ALL':
            conditions.append("r.room_type = %s")
            params.append(room_type)

        if min_capacity and int(min_capacity) > 0:
            conditions.append("r.capacity >= %s")
            params.append(int(min_capacity))

        sql = f"""
            SELECT r.*
            FROM rooms r
            WHERE {' AND '.join(conditions)}
            ORDER BY r.price_per_night ASC, CAST(r.room_number AS UNSIGNED) ASC
        """
        return query_all(sql, tuple(params))

    @staticmethod
    def get_statistics():
        """Get room counts grouped by current availability and status."""
        sql = """
            SELECT 
                COUNT(*) AS total_rooms,
                SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
                SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
                SUM(CASE WHEN status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms
            FROM rooms
        """
        res = query_one(sql)
        if not res:
            return {'total_rooms': 0, 'available_rooms': 0, 'occupied_rooms': 0, 'maintenance_rooms': 0}
        return {
            'total_rooms': res['total_rooms'] or 0,
            'available_rooms': res['available_rooms'] or 0,
            'occupied_rooms': res['occupied_rooms'] or 0,
            'maintenance_rooms': res['maintenance_rooms'] or 0
        }

    @staticmethod
    def get_room_types_distribution():
        """Get count of rooms by type for dashboard / reports charts."""
        sql = """
            SELECT room_type, COUNT(*) AS count
            FROM rooms
            GROUP BY room_type
            ORDER BY count DESC
        """
        return query_all(sql)

    @staticmethod
    def sync_daily_occupancy():
        """
        Optional helper to keep room status synchronized with today's date.
        If a room is under Maintenance, keep Maintenance.
        If a room has an active booking today (check_in <= TODAY < check_out) with CONFIRMED or CHECKED_IN,
        set to Occupied; otherwise Available.
        """
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Mark rooms occupied if currently in an active stay
                cursor.execute("""
                    UPDATE rooms r
                    SET r.status = 'Occupied'
                    WHERE r.status != 'Maintenance'
                    AND r.id IN (
                        SELECT b.room_id FROM bookings b
                        WHERE b.status IN ('CONFIRMED', 'CHECKED_IN')
                          AND b.check_in <= CURDATE()
                          AND b.check_out > CURDATE()
                    )
                """)
                # Mark rooms available if no active stay today
                cursor.execute("""
                    UPDATE rooms r
                    SET r.status = 'Available'
                    WHERE r.status = 'Occupied'
                    AND r.id NOT IN (
                        SELECT b.room_id FROM bookings b
                        WHERE b.status IN ('CONFIRMED', 'CHECKED_IN')
                          AND b.check_in <= CURDATE()
                          AND b.check_out > CURDATE()
                    )
                """)
