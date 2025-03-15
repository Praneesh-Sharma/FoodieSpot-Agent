from crewai import Agent
from agents.database import DatabaseAgent

class RecommendationAgent:
    def __init__(self):
        self.db_agent = DatabaseAgent()
        self.agent = Agent(
            name="Restaurant Recommender",
            role="A helpful AI assistant for restaurant recommendations.",
            goal="Help users find restaurants based on location and cuisine.",
            backstory="An AI trained on thousands of restaurant reviews and customer preferences."
        )

    def _fetch_recommendations(self, location, cuisine):
        """Mock function to simulate fetching restaurant recommendations."""
        return [{"name": "Spicy Treat", "location": location, "cuisine": cuisine}]

    def recommend(self, location, cuisine=None):
        """Uses DatabaseAgent to fetch restaurant recommendations."""
        # print(f"Debug: Received request for location={location}, cuisine={cuisine}")
        recommendations = self._fetch_recommendations(location, cuisine)
        
        # Debugging: Print output before returning
        # print(f"Debug: Recommendations fetched: {recommendations}")

        return recommendations if isinstance(recommendations, list) else []