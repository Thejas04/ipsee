import requests

# Backend URL (ensure this is the correct endpoint for your backend)
backend_url = "https://ip-see.com/api/report"  # Update to correct URL if different

# Simulate the extracted TOS text and cookie options (as extracted from content.js for Demo 4)
tos_text = """
We use cookies to collect personal information such as your browsing history, location, and preferences. By clicking "Accept All", you consent to all data collection activities. Learn more in our Terms of Service.

Terms of Service:
Data Collection & Personal Information:
By accepting all cookies, you agree to allow this website to collect personal data, including:
    - Your browsing history
    - Your IP address and location
    - Your personal preferences and interests
    - Data shared with third-party advertisers

We may also share this information with third-party partners for marketing, advertising, and analysis purposes.
This data may be retained for extended periods and used to build a profile for personalized advertising.
"""

cookie_options = "Accept All Cookies"

# The website URL being analyzed
website_url = "https://demo.ip-see.com:8443/demo4"

# Prepare the data to send
data_to_send = {
    "url": website_url,
    "txtTos": tos_text,  # Make sure this key is named 'txtTos' as expected by the backend
    "options": cookie_options  # Ensure this key is named 'options'
}

# Send a POST request to the backend
try:
    print("Data being sent to backend:")
    print(data_to_send)  # For debugging purposes

    response = requests.post(backend_url, json=data_to_send)

    # Check if the request was successful
    if response.status_code == 200:
        print("Data successfully sent to the backend:")
        print(response.json())  # Output the backend's response
    else:
        print(f"Error sending data to backend: {response.status_code}")
        print(response.text)  # Print any error message
except Exception as e:
    print(f"An error occurred: {e}")
