import streamlit as st
import requests
import uuid
import json

# Hardcoded API request parameters
API_URL = "http://127.0.0.1:8000/answer"


def send_request(message):
    request_id = str(uuid.uuid4())
    payload = {"question": message, "request_id": request_id}
    print(
        "Request Payload:", json.dumps(payload, indent=4)
    )  # Print the request payload in a formatted manner
    response = requests.post(API_URL, json=payload)
    print(
        "Response JSON:", json.dumps(response.json(), indent=4)
    )  # Print the entire response JSON formatted for readability
    return response.json()


def main():
    st.title("Analytics")

    # Input field for user message
    user_message = st.text_input("Enter your question:")

    if st.button("Submit"):
        if user_message.strip():
            with st.spinner("Sending request..."):
                response = send_request(user_message)

            if response.get("status") == "SUCCESS":
                st.success("Response received!")
                response_message = response.get(
                    "message", "No response message available."
                )
                st.markdown(f"{response_message}")

                # Add collapsible section to show full JSON response
                with st.expander("View Full Response JSON"):
                    st.json(response)
            else:
                st.error("Failed to fetch the response.")
                error_details = response.get("error", "No error details available.")
                st.markdown(f"**Error Details:** {error_details}")
        else:
            st.warning("Please enter a message before submitting.")


if __name__ == "__main__":
    main()
