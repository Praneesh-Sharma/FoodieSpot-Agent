# agents/chat.py
import os
import json
import requests
import re

from .recommendation import RecommendationAgent
from .reservation import ReservationAgent

class ChatAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Set it in .env or as an environment variable.")

        self.recommendation_agent = RecommendationAgent()
        self.reservation_agent = ReservationAgent()
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        self.conversation_state = {}

    def extract_intent(self, user_input):
        intent = self.classify_intent(user_input)
        print(f"DEBUG: Intent classified as: {intent}")
        new_details = {}
        if intent == "restaurants":
            new_details = self.extract_restaurant_details(user_input)
        elif intent == "reservation":
            new_details = {}

        if new_details is None:
            print(f"DEBUG: New details are None for intent: {intent}")
            return {"intent": intent}

        for key, value in new_details.items():
            if value and value != "null":
                self.conversation_state[key] = value

        self.conversation_state["intent"] = intent
        return self.conversation_state

    def classify_intent(self, user_input):
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": (
                    "ONLY determine if the user is looking for 'restaurants' or 'reservation'. "
                    "Respond only with a JSON object containing {'intent': <value>}, where <value> is either 'restaurants' or 'reservation'. "
                    "If the intent is unclear, return {'intent': null}. "
                    f"User input: {user_input}"
                )
            }]
        }
        response = requests.post(self.groq_api_url, headers=self.headers, json=payload)
        print(f"DEBUG: API request status for intent: {response.status_code}")
        if response.status_code == 200:
            try:
                raw_response = response.json()["choices"][0]["message"]["content"].strip()
                print(f"DEBUG: Raw intent response from API: {raw_response}")
                # Extract JSON using regex to handle extra text
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    print(f"DEBUG: Extracted intent JSON: {json_str}")
                    intent_data = json.loads(json_str)
                    intent = intent_data.get("intent")
                    print(f"DEBUG: Parsed intent: {intent}")
                    return intent if intent in ["restaurants", "reservation"] else None
                else:
                    print("DEBUG: No JSON found in intent response")
                    return None
            except (json.JSONDecodeError, KeyError) as e:
                print(f"DEBUG: Intent parsing error: {e}")
                print(f"DEBUG: Raw API response: {response.text}")
                return None
        print(f"DEBUG: API error in classify_intent: {response.status_code} - {response.text}")
        return None

    def extract_restaurant_details(self, user_input):
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": (
                    "**Donot** fetch details on your own, only focus on the user input "
                    "**Only extract** structured details in JSON format with keys: 'city', 'cuisine' "
                    "If any detail is missing, return it as null. Donot make any assumptions"
                    "Strictly return only a pure JSON object with no extra text."
                    f"User input: {user_input}"
                )
            }]
        }
        response = requests.post(self.groq_api_url, headers=self.headers, json=payload)
        print(f"DEBUG: API request status: {response.status_code}")
        if response.status_code == 200:
            try:
                raw_response = response.json()["choices"][0]["message"]["content"].strip()
                print(f"DEBUG: Raw API response: {raw_response}")
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    print(f"DEBUG: Extracted JSON string: {json_str}")
                    details = json.loads(json_str)
                    print(f"DEBUG: Parsed details: {details}")
                    city = details.get("city")
                    cuisine = details.get("cuisine")
                    print(f"DEBUG: Extracted city: {city}, cuisine: {cuisine}")
                    recommendations = self.recommendation_agent.recommend(city, cuisine) if city else []
                    print(f"DEBUG: Recommendations: {recommendations}")
                    # Return full recommendations without filtering 'id'
                    return {"city": city, "cuisine": cuisine, "recommendations": recommendations}
                else:
                    print("DEBUG: No JSON found in response")
                    return {"city": None, "cuisine": None, "recommendations": []}
            except (json.JSONDecodeError, KeyError) as e:
                print(f"DEBUG: Parsing error in extract_restaurant_details: {e}")
                print(f"DEBUG: Raw API response: {response.text}")
                return {"city": None, "cuisine": None, "recommendations": []}
        print(f"DEBUG: API error in extract_restaurant_details: {response.status_code} - {response.text}")
        return {"city": None, "cuisine": None, "recommendations": []}

    def extract_reservation_details(self, restaurant_name, date, time, num_people):
        if not all([restaurant_name, date, time, num_people]):
            return {"time": None, "date": None, "num_people": None, "restaurant_name": None}

        try:
            date_str = date.strftime("%Y-%m-%d")
            time_str = time.strftime("%H:%M:%S")
            num_people_int = int(num_people)
            if num_people_int < 1:
                raise ValueError("Number of people must be at least 1")
        except (AttributeError, ValueError) as e:
            return {"time": None, "date": None, "num_people": None, "restaurant_name": None}

        return {
            "restaurant_name": restaurant_name,
            "date": date_str,
            "time": time_str,
            "num_people": num_people_int
        }