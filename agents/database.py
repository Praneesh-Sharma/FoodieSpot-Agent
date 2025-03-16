# agents/database.py
from sqlalchemy import text
from database.connect import get_db
from database.queries import GET_RESTAURANTS_BY_CITY_FOOD, CHECK_RESTAURANT_AVAILABILITY, CHECK_TABLE_AVAILABILITY, BOOK_TABLE
import sqlite3

class DatabaseAgent:
    def __init__(self):
        self.db = next(get_db())

    def find_restaurants(self, city, food_type):
        query = text("""
        SELECT id, name, location, cuisine 
        FROM restaurants 
        WHERE location = :city AND cuisine ILIKE :food_type;
        """)
        params = {"city": city, "food_type": f"%{food_type}%"}
        result = self.db.execute(query, params).fetchall()
        return result

    def is_restaurant_open(self, restaurant_id, reservation_time):
        """Check if the restaurant is open at the given time."""
        result = self.db.execute(CHECK_RESTAURANT_AVAILABILITY, (restaurant_id,)).fetchone()
        if result:
            open_time, close_time = result
            return open_time <= reservation_time <= close_time
        return False

    def is_table_available(self, restaurant_id, reservation_time):
        """Check if a table is available at the given time."""
        result = self.db.execute(CHECK_TABLE_AVAILABILITY, (restaurant_id, reservation_time)).fetchone()
        return result[0] == 0

    def book_table(self, restaurant_id, reservation_time):
        """Book a table if available."""
        if not self.is_restaurant_open(restaurant_id, reservation_time):
            return "Restaurant is closed at this time."

        if not self.is_table_available(restaurant_id, reservation_time):
            return "No tables available at this time."

        try:
            self.db.execute(BOOK_TABLE, (restaurant_id, reservation_time))
            self.db.commit()
            return "Reservation successful!"
        except Exception as e:
            print(f"Error booking table: {e}")
            return "Error making reservation."
        
    def fetch(self, query, params=None):
        """Executes a SELECT query and returns the results."""
        result = self.db.execute(text(query), params).fetchall()
        return result

    def insert(self, query, params=None):
        """Executes an INSERT query and returns the last inserted ID."""
        try:
            result = self.db.execute(text(query), params)
            self.db.commit()
            return result.lastrowid  # Returns the ID of the last inserted row
        except Exception as e:
            print(f"Error inserting data: {e}")
            return None
