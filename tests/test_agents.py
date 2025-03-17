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
    # print("RecommendationAgent Output:", result)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)
    logger.info("RecommendationAgent test passed.")
    print("RecommendationAgent test passed.")

def test_reservation_agent_check_availability():
    logger.info("Testing ReservationAgent check_availability...")
    res_agent = ReservationAgent()
    result = res_agent.check_availability(1, "2025-03-16", "18:00:00", 2)  # Added a sample date
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
    logger.info(f"Booking result: {result}")  # Log the response
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "status" in result, "Missing 'status' key in response"
    assert result["status"] in ["success", "failed"], "Invalid status value"
    logger.info("ReservationAgent booking test passed.")
    print("ReservationAgent booking test passed.")

if __name__ == "__main__":
    test_recommendation_agent()
    # test_reservation_agent_check_availability()
    # test_reservation_agent_book()
        