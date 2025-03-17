import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agents.recommendation import RecommendationAgent
from agents.reservation import ReservationAgent
from logs.logger import logger 

logger.info("Starting test_agents execution...")

def test_recommendation_agent():
    logger.info("Testing RecommendationAgent...")
    rec_agent = RecommendationAgent()
    result = rec_agent.recommend("Mumbai", "Indian")
    print("RecommendationAgent Output:", result)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)
    logger.info("RecommendationAgent test passed.")
    print("RecommendationAgent test passed.")

def test_reservation_agent_check_availability():
    logger.info("Testing ReservationAgent check_availability...")
    res_agent = ReservationAgent()
    result = res_agent.check_availability(1, "2025-03-16", "18:00:00", 6)  # Added a sample date
    print("ReservationAgent Output: ", result)
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "available" in result, "Missing 'available' key in response"
    assert "message" in result, "Missing 'message' key in response"
    assert isinstance(result["available"], bool), f"Expected 'available' to be boolean, but got {type(result['available'])}"
    logger.info("ReservationAgent availability check test passed.")
    print("ReservationAgent availability check test passed.")

def test_reservation_agent_book():
    logger.info("Testing ReservationAgent book_table...")
    res_agent = ReservationAgent()
    result = res_agent.book_table(1, 5, "Demo User", "9812345670", 2, "2025-03-17", "18:00:00")  # Fixed parameters
    print(result)
    logger.info(f"Booking result: {result}")  # Log the response
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "status" in result, "Missing 'status' key in response"
    assert result["status"] in ["success", "failed"], "Invalid status value"
    logger.info("ReservationAgent booking test passed.")
    print("ReservationAgent booking test passed.")

def test_reservation_agent_all():
    logger.info("Testing ReservationAgent with user input for booking...")
    res_agent = ReservationAgent()

    # Check availability
    restaurant_id = 1
    num_people = 4
    date = "2025-03-18"
    time = "19:00:00"

    availability = res_agent.check_availability(restaurant_id, date, time, num_people)
    print("Availability Check Output:", availability)

    if not availability["available"]:
        print("No tables available. Test ending.")
        return  # Stop execution if no availability

    customer_name = input("Enter your name: ")
    customer_contact = input("Enter your phone number: ")
    
    available_tables = availability.get("available_tables", [])
    if available_tables:
        available_table_id = available_tables[0]["id"]  # Directly access key
    else:
        print("No tables available.")
        return
    
    if not available_table_id:
        print("No specific table found. Please check database.")
        return

    print("\nBooking Details:")
    print(f"Restaurant ID: {restaurant_id}")
    print(f"Table ID: {available_table_id}")
    print(f"Customer Name: {customer_name}")
    print(f"Customer Contact: {customer_contact}")
    print(f"Number of People: {num_people}")
    print(f"Date: {date}")
    print(f"Time: {time}")

    confirmation = input("Do you want to proceed with the booking? (yes/no): ").strip().lower()
    if confirmation != "yes":
        print("Booking cancelled.")
        return

    result = res_agent.book_table(restaurant_id, available_table_id, customer_name, customer_contact, num_people, date, time)
    
    logger.info(f"Booking Result: {result}")
    print("Final Booking Output:", result)


if __name__ == "__main__":
    test_recommendation_agent()
    # test_reservation_agent_check_availability()
    # test_reservation_agent_book()
    # test_reservation_agent_all()
        