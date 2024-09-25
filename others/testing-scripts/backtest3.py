import requests

# Backend URL (ensure this is the correct endpoint for your backend)
backend_url = "https://ip-see.com/api/report"  # Update to correct URL if different

# Simulate the extracted TOS text and cookie options (as extracted from content.js for Demo 3)
tos_text = """
This website requires essential cookies for core functionality. By continuing, you agree to our Terms of Service.

Terms of Service:
Essential Cookies Required for Functionality:
This website uses essential cookies that are strictly necessary for the operation of our services. These include cookies related to session management, authentication, and secure browsing, which allow you to navigate the website and use its features.
Without these essential cookies, certain parts of the website may not function correctly, such as logging in, maintaining your session, or completing transactions.
By accepting essential cookies, you enable core functionalities such as the ability to log in, access secure areas, and use personalized settings. Essential cookies do not track your browsing behavior for marketing purposes.
If you choose to reject these cookies, some website functions may be unavailable, and the user experience may be diminished.
"""

cookie_options = "Accept All Cookies | Accept Essential Cookies | Reject All Cookies"

# The website URL being analyzed
website_url = "https://demo.ip-see.com:8443/demo3"

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
