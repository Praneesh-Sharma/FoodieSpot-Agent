# frontend/app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import datetime
from agents.chat import ChatAgent

def main():
    st.title("FoodieSpot Reservation System")

    # Initialize ChatAgent
    if "chat_agent" not in st.session_state:
        st.session_state.chat_agent = ChatAgent()

    # Initialize conversation state and chat history
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "show_reservation_form" not in st.session_state:
        st.session_state.show_reservation_form = False
    if "availability_checked" not in st.session_state:
        st.session_state.availability_checked = False
    if "availability_result" not in st.session_state:
        st.session_state.availability_result = None
    if "reservation_details" not in st.session_state:
        st.session_state.reservation_details = {}

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("How can I assist you today?"):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Update conversation state with agent's response
        intent_data = st.session_state.chat_agent.extract_intent(prompt)
        print(f"DEBUG: Intent data from extract_intent: {intent_data}")
        st.session_state.conversation_state.update(intent_data)
        print(f"DEBUG: Conversation state after update: {st.session_state.conversation_state}")

        # Build the assistant's response dynamically
        assistant_response = ""
        with st.chat_message("assistant"):
            if intent_data.get("intent") == "restaurants":
                assistant_response = "Here are some restaurant recommendations:\n"
                recommendations = intent_data.get("recommendations", [])
                print(f"DEBUG: Recommendations before processing: {recommendations}")
                if recommendations:
                    for rec in recommendations:
                        name = rec.get('name', 'Unknown Restaurant')
                        cuisine = rec.get('cuisine', 'Unknown Cuisine')
                        location = rec.get('location', 'Unknown Location')
                        assistant_response += f"- {name}: {cuisine}\n"
                    st.session_state.conversation_state["recommendations"] = recommendations  # Explicitly preserve
                    print(f"DEBUG: Recommendations stored in conversation_state: {recommendations}")
                else:
                    assistant_response += "No recommendations found."
                st.write(assistant_response)
                st.session_state.show_reservation_form = False
                st.session_state.availability_checked = False
                st.session_state.availability_result = None
                st.session_state.reservation_details = {}
            elif intent_data.get("intent") == "reservation":
                assistant_response = "Let's make a reservation. Please fill in the details below:"
                st.write(assistant_response)
                st.session_state.show_reservation_form = True
                st.session_state.availability_checked = False
                st.session_state.availability_result = None
                st.session_state.reservation_details = {}
            else:
                assistant_response = "I couldn't understand your intent. Do you want restaurant recommendations or to make a reservation?"
                st.write(assistant_response)
                st.session_state.show_reservation_form = False
                st.session_state.availability_checked = False
                st.session_state.availability_result = None

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

    # Display reservation form if triggered
    if st.session_state.show_reservation_form:
        with st.chat_message("assistant"):
            recommendations = st.session_state.conversation_state.get("recommendations", [])
            if not recommendations:
                st.write("Please get restaurant recommendations first by asking something like 'places to eat in <city>'.")
                if st.button("Close", key="close_form"):
                    st.session_state.show_reservation_form = False
            else:
                st.write("Reservation Form:")

                # Step 1: Initial form for availability check
                if not st.session_state.availability_checked:
                    restaurant_names = [r.get("name", "Unknown") for r in recommendations]
                    
                    # Retain previous values if they exist
                    default_restaurant = st.session_state.reservation_details.get("restaurant_name", restaurant_names[0])
                    default_date = st.session_state.reservation_details.get("date", datetime(2025, 1, 1))
                    default_time = st.session_state.reservation_details.get("time", None)
                    default_num_people = st.session_state.reservation_details.get("num_people", 1)

                    restaurant_name = st.selectbox("Restaurant Name", restaurant_names, index=restaurant_names.index(default_restaurant) if default_restaurant in restaurant_names else 0, key="res_name")
                    date = st.date_input("Date", min_value=datetime(2025, 1, 1), value=default_date, key="res_date")
                    time = st.time_input("Time", value=default_time if default_time else None, key="res_time")
                    num_people = st.number_input("Number of People", min_value=1, step=1, value=default_num_people, key="res_people")

                    if st.button("Check Availability", key="check_availability"):
                        reservation_details = st.session_state.chat_agent.extract_reservation_details(
                            restaurant_name=restaurant_name,
                            date=date,
                            time=time,
                            num_people=num_people
                        )
                        # Debug prints for user input
                        print(f"DEBUG: User input - Restaurant Name: {restaurant_name}")
                        print(f"DEBUG: User input - Date: {date}")
                        print(f"DEBUG: User input - Time: {time}")
                        print(f"DEBUG: User input - Number of People: {num_people}")
                        print(f"DEBUG: Extracted reservation details: {reservation_details}")

                        st.session_state.reservation_details = reservation_details
                        
                        # Get restaurant_id from recommendations
                        recommendations = st.session_state.conversation_state.get("recommendations", [])
                        print(f"DEBUG: Current recommendations in conversation_state: {recommendations}")
                        print(f"DEBUG: Looking for restaurant name: '{restaurant_name}'")
                        restaurant_id = next((r.get("id") for r in recommendations if r.get("name") == restaurant_name), None)
                        print(f"DEBUG: Restaurant ID from recommendations: {restaurant_id}")
                        if restaurant_id is None:
                            st.write("Error: Could not find restaurant ID. This should not happen with a valid selection.")
                            print(f"DEBUG: Available restaurant names: {[r.get('name') for r in recommendations]}")
                            st.session_state.availability_checked = False
                            st.session_state.availability_result = None
                        else:
                            availability = st.session_state.chat_agent.reservation_agent.check_availability(
                                restaurant_id=restaurant_id,
                                date=reservation_details["date"],
                                time=reservation_details["time"],
                                num_people=reservation_details["num_people"]
                            )
                            st.session_state.availability_result = availability
                            st.session_state.availability_checked = True
                            st.write(f"Availability: {availability['message']}")

                # Step 2: Show customer details form if available
                elif st.session_state.availability_checked and st.session_state.availability_result["available"]:
                    st.write(f"Availability: {st.session_state.availability_result['message']}")
                    
                    # Retain previous inputs
                    restaurant_name = st.selectbox("Restaurant Name", [st.session_state.reservation_details["restaurant_name"]], disabled=True, key="res_name_locked")
                    date = st.date_input("Date", value=datetime.strptime(st.session_state.reservation_details["date"], "%Y-%m-%d"), disabled=True, key="res_date_locked")
                    time = st.time_input("Time", value=datetime.strptime(st.session_state.reservation_details["time"], "%H:%M:%S").time(), disabled=True, key="res_time_locked")
                    num_people = st.number_input("Number of People", value=st.session_state.reservation_details["num_people"], disabled=True, key="res_people_locked")
                    
                    customer_name = st.text_input("Your Name", key="res_customer_name")
                    customer_contact = st.text_input("Your Contact (e.g., phone or email)", key="res_customer_contact")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm Reservation", key="confirm_reservation"):
                            if customer_name and customer_contact:
                                # Get restaurant_id from recommendations
                                recommendations = st.session_state.conversation_state.get("recommendations", [])
                                restaurant_id = next((r.get("id") for r in recommendations if r.get("name") == st.session_state.reservation_details["restaurant_name"]), None)
                                print(f"DEBUG: Restaurant ID for booking: {restaurant_id}")
                                
                                if restaurant_id is None:
                                    st.write("Error: Could not find restaurant ID for booking.")
                                else:
                                    # Use first available table
                                    table_id = st.session_state.availability_result["available_tables"][0]["id"]
                                    
                                    reservation_response = st.session_state.chat_agent.reservation_agent.book_table(
                                        restaurant_id=restaurant_id,
                                        table_id=table_id,
                                        customer_name=customer_name,
                                        customer_contact=customer_contact,
                                        num_people=st.session_state.reservation_details["num_people"],
                                        date=st.session_state.reservation_details["date"],
                                        time=st.session_state.reservation_details["time"]
                                    )
                                    reservation_message = f"Reservation Response: {reservation_response['message'] if reservation_response['status'] == 'failed' else 'Success - Reservation ID: ' + str(reservation_response['reservation_id'])}"
                                    st.write(reservation_message)
                                    st.session_state.chat_history.append({"role": "assistant", "content": reservation_message})
                                    st.session_state.show_reservation_form = False
                                    st.session_state.availability_checked = False
                                    st.session_state.availability_result = None
                                    st.session_state.reservation_details = {}
                            else:
                                st.write("Please provide your name and contact details.")
                    with col2:
                        if st.button("Cancel", key="res_cancel"):
                            st.session_state.show_reservation_form = False
                            st.session_state.availability_checked = False
                            st.session_state.availability_result = None
                            st.session_state.reservation_details = {}
                
                # If no availability, show message and allow retry
                elif st.session_state.availability_checked and not st.session_state.availability_result["available"]:
                    st.write(f"Availability: {st.session_state.availability_result['message']}")
                    if st.button("Try Different Details", key="retry"):
                        st.session_state.availability_checked = False
                        st.session_state.availability_result = None

if __name__ == "__main__":
    main()