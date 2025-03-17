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

    def recommend(self, location, cuisine=None):
        """Fetch actual restaurant recommendations from the database."""
        print(f"Debug: Querying for location={location}, cuisine={cuisine if cuisine else 'Any'}")
        recommendations = self.db_agent.find_restaurants(location, cuisine if cuisine else "")
            
        # Convert query results into a list of dictionaries
        formatted_recommendations = [
            {"name": r[1], "location": r[2], "cuisine": r[3]} for r in recommendations
        ]
        # print(f"Debug: Recommendations fetched: {formatted_recommendations}")
        
        if cuisine and formatted_recommendations:
            formatted_recommendations = [
                r for r in formatted_recommendations if r["cuisine"].lower() == cuisine.lower()
            ]

        return formatted_recommendations if formatted_recommendations else []
    