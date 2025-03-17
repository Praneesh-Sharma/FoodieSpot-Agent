import os
import json
import requests
import re
from datetime import datetime
from .recommendation import RecommendationAgent
from .reservation import ReservationAgent


class Agent:
    """Defines the AI Agent with a name, role, goal, and backstory."""
    def __init__(self, name, role, goal, backstory):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory


class ChatAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Set it in .env or as an environment variable.")

        self.recommendation_agent = RecommendationAgent()
        self.reservation_agent = ReservationAgent()
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        # Defining the Chat Agent
        self.agent = Agent(
            name="Restaurant Assistant",
            role="An AI assistant for restaurant recommendations and reservations.",
            goal="Extract data from user prompts",
            backstory="Was built to extact details and then return a JSON object"
        )

        self.conversation_state = {}


    def extract_intent(self, user_input):
        """Determines if the user wants to find restaurants or book a table."""
        intent = self.classify_intent(user_input)  # Calls Groq to classify intent

        if intent == "restaurants":
            new_details = self.extract_restaurant_details(user_input)
        elif intent == "reservation":
            new_details = self.extract_reservation_details(user_input)
        else:
            return {"intent": intent}  # If intent is unrecognized, return it as is

        # Update the conversation state with any new details
        for key, value in new_details.items():
            if value and value != "null":  # Keep old values if new ones are empty/null
                self.conversation_state[key] = value

        # Ensure the intent is stored
        self.conversation_state["intent"] = intent

        return self.conversation_state  # Return updated conversation state
        
        
    def classify_intent(self, user_input):
        """Uses Groq to determine if the user wants restaurants or a table booking."""
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": (
                    "Determine if the user is looking for 'restaurants' or 'reservation'. "
                    "Respond only with a JSON object containing {'intent': <value>}, where <value> is either 'restaurants' or 'reservation'. "
                    "Strictly give only the JSON object"
                    f"User input: {user_input}"
                )
            }]
        }

        response = requests.post(self.groq_api_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            try:
                groq_response = response.json()
                
                # Ensure response has expected structure
                if not groq_response or "choices" not in groq_response:
                    raise ValueError("Empty or malformed response from Groq API.")

                message_content = groq_response["choices"][0]["message"]["content"].strip()

                # Remove code block formatting (```json ... ```)
                message_content = re.sub(r'```json\n(.*?)\n```', r'\1', message_content, flags=re.DOTALL)
                message_content = re.sub(r'```(.*?)```', r'\1', message_content, flags=re.DOTALL)

                # Remove single backticks around JSON (if present)
                message_content = re.sub(r'^`(.*)`$', r'\1', message_content, flags=re.DOTALL)

                # Parse JSON
                intent = json.loads(message_content).get("intent")  

                if intent in ["restaurants", "reservation"]:
                    return intent

                raise ValueError(f"Unexpected intent: {intent}")

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Parsing Error: {e}")
                print(f"Groq Raw Response: {response.text}")
                return None

        print(f"API Error: {response.status_code} - {response.text}")
        return None


    def extract_restaurant_details(self, user_input):
        """Uses Groq to extract city, cuisine, num_people, and time if the intent is restaurants."""
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": (
                    "**Only extract** structured details in JSON format with keys: "
                    "'city', 'cuisine', 'num_people', and 'time' in in HH:MM:SS format. "
                    "If any detail is missing, return it as null. "
                    "Strictly return only a pure JSON object with no extra text. "
                    "**Donot** fetch details on your own, only focus on th user input"
                    f"User input: {user_input}"
                )
            }]
        }

        response = requests.post(self.groq_api_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            try:
                groq_response = response.json()["choices"][0]["message"]["content"].strip()

                # Ensure JSON-only response by removing backticks or text artifacts
                json_match = re.search(r'\{.*\}', groq_response, re.DOTALL)
                if json_match:
                    json_string = json_match.group(0)  # Extract only the JSON part
                    details = json.loads(json_string)

                return {
                    "city": details.get("city"),
                    "cuisine": details.get("cuisine"),
                    "num_people": details.get("num_people"),
                    "time": details.get("time")
                }

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Parsing Error: {e}")
                print(f"Groq Raw Response: {response.text}")  # Debugging
                return {"city": None, "cuisine": None, "num_people": None, "time": None}

        print(f"API Error: {response.status_code} - {response.text}")
        return {"city": None, "cuisine": None, "num_people": None, "time": None}  # Default on failure


    def extract_reservation_details(self, user_input):
        """Uses Groq to extract reservation details: time, date, num_people, and restaurant_name."""
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": (
                    "Extract structured details in JSON format with keys: "
                    "'time', 'date', 'num_people', and 'restaurant_name'. "
                    "return time in HH:MM:SS and date in 2025-MM-DD format if given"
                    "If any detail is missing, return it as null. "
                    "Strictly return only a pure JSON object with no extra text. "
                    f"User input: {user_input}"
                )
            }]
        }

        response = requests.post(self.groq_api_url, headers=self.headers, json=payload)

        if response.status_code == 200:
            try:
                groq_response = response.json()["choices"][0]["message"]["content"].strip()

                # Clean and extract JSON response
                json_match = re.search(r'\{.*\}', groq_response, re.DOTALL)
                if json_match:
                    json_string = json_match.group(0)  # Extract only the JSON part
                    details = json.loads(json_string)

                # Default date to today if not provided
                if not details.get("date") or details.get("date") == "null":
                    details["date"] = datetime.today().strftime("%Y-%m-%d")

                return {
                    "time": details.get("time"),
                    "date": details.get("date"),
                    "num_people": details.get("num_people"),
                    "restaurant_name": details.get("restaurant_name")
                }

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Parsing Error: {e}")
                print(f"Groq Raw Response: {response.text}")  # Debugging
                return {"time": None, "date": datetime.today().strftime("%Y-%m-%d"), "num_people": None, "restaurant_name": None}

        print(f"API Error: {response.status_code} - {response.text}")
        return {"time": None, "date": datetime.today().strftime("%Y-%m-%d"), "num_people": None, "restaurant_name": None}  # Default on failure

    
    def chat(self):
        """Interactive chat loop where the agent processes input dynamically."""
        print(f"Welcome! I am {self.agent.name}. How can I assist you today?")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            intent_data = self.extract_intent(user_input)
            # response = self.handle_intent(intent_data)
            print(f"🤖 Bot: {intent_data}")


if __name__ == "__main__":
    chat_agent = ChatAgent()
    chat_agent.chat()
