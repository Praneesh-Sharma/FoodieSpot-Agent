from crewai import Agent
from agents.database import DatabaseAgent

class ReservationAgent:
    def __init__(self):
        self.db_agent = DatabaseAgent()
        self.agent = Agent(
            name="Reservation Manager",
            role="Handles restaurant reservations and availability checks.",
            goal="Ensure smooth restaurant reservations for users.",
            backstory="An AI-powered agent trained in restaurant management and customer service."
        )

    def check_availability(self, restaurant_id, date, time):
        """Checks if a table is available at the given restaurant, date, and time."""
        query = """
        SELECT table_id FROM reservations
        WHERE restaurant_id = :restaurant_id AND reservation_time = :reservation_time AND status = 'confirmed'
        """
        booked_tables = self.db_agent.fetch(query, {"restaurant_id": restaurant_id, "reservation_time": f"{date} {time}"})
        
        if booked_tables:
            return {"available": False, "message": "No tables available at this time."}
        return {"available": True, "message": "Tables are available for booking."}

    def book_table(self, restaurant_id, table_id, customer_name, customer_contact, date, time):
        """Books a table for a customer at a restaurant."""
        availability = self.check_availability(restaurant_id, date, time)
        
        if not availability["available"]:
            return {"status": "failed", "message": "No available tables at this time."}

        insert_query = """
        INSERT INTO reservations (restaurant_id, table_id, customer_name, customer_contact, reservation_time, status, created_at)
        VALUES (:restaurant_id, :table_id, :customer_name, :customer_contact, :reservation_time, 'pending', NOW())
        RETURNING id;
        """
        
        reservation_id = self.db_agent.insert(insert_query, {
            "restaurant_id": restaurant_id,
            "table_id": table_id,
            "customer_name": customer_name,
            "customer_contact": customer_contact,
            "reservation_time": f"{date} {time}"
        })
        
        if reservation_id:
            return {
                "status": "success",
                "reservation_id": reservation_id,
                "restaurant_id": restaurant_id,
                "table_id": table_id,
                "customer_name": customer_name,
                "customer_contact": customer_contact,
                "reservation_time": f"{date} {time}"
            }
        return {"status": "failed", "message": "Could not complete the reservation."}
