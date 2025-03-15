import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agents.recommendation import RecommendationAgent
from agents.reservation import ReservationAgent

def test_recommendation_agent():
    rec_agent = RecommendationAgent()
    result = rec_agent.recommend("Mumbai", "Indian")
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)
    print("✅ RecommendationAgent test passed.")

def test_reservation_agent_check_availability():
    res_agent = ReservationAgent()
    result = res_agent.check_availability(1, "2025-03-16", "18:00:00")  # Added a sample date
    assert isinstance(result, str)
    print("✅ ReservationAgent availability check test passed.")

def test_reservation_agent_book():
    res_agent = ReservationAgent()
    result = res_agent.book_table(1, "2024-03-17", "18:00:00")
    assert isinstance(result, dict), f"Expected dict, but got {type(result)}"
    assert "status" in result, "Missing 'status' key in response"
    print("✅ ReservationAgent booking test passed.")

if __name__ == "__main__":
    test_recommendation_agent()
    test_reservation_agent_check_availability()
    test_reservation_agent_book()