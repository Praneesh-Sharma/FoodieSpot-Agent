# database/queries.py

GET_RESTAURANTS_BY_CITY_FOOD = """
SELECT id, name, city, cuisine_type FROM restaurants 
WHERE city = %s AND cuisine_type ILIKE %s;
"""

CHECK_RESTAURANT_AVAILABILITY = """
SELECT open_time, close_time FROM restaurants WHERE id = %s;
"""

CHECK_TABLE_AVAILABILITY = """
SELECT COUNT(*) FROM reservations 
WHERE restaurant_id = %s AND reservation_time = %s;
"""

BOOK_TABLE = """
INSERT INTO reservations (restaurant_id, reservation_time) 
VALUES (%s, %s) RETURNING id;
"""
