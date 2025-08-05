import os
import sys

# Add /Users/pei-yiliu/EngageAI/module to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from moodle_shared.function_name.ClassMoodleService import *

def main():
    # Step 1: Initialize the MoodleService class
    MOODLE_URL = "https://moodle.c3l.ai"
    TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
    moodle = MoodleService(MOODLE_URL, TOKEN)

    # Step 2: Get the users
    users = moodle.get_users()

    # Step 3: Print user information
    for user in users:
        print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user.get('email', 'N/A')}")

if __name__ == "__main__":
    main()








# import requests
# import json

# def get_moodle_users(moodle_url, token, function="core_user_get_users", search_query="%"):

#     url = f"{moodle_url}/webservice/rest/server.php"

#     params = {
#         "wstoken": token,
#         "wsfunction": function,
#         "moodlewsrestformat": "json"
#     }

#     data = {
#         "criteria[0][key]": "firstname",
#         "criteria[0][value]": search_query,
#     }

#     response = requests.post(url, params=params, data=data)

#     if response.status_code == 200:
#         result = response.json()
#         return result.get("users", [])
#     else:
#         print(f"Error: {response.status_code} - {response.text}")
#         return []

# # Example usage
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# users = get_moodle_users(MOODLE_URL, TOKEN)

# for user in users:
#     print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user['email']}")



# # Step 1: Initialize the MoodleService class
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"

# moodle = MoodleService(MOODLE_URL, TOKEN)
# users = moodle.get_users()  

# # Step 3: Print the user information
# for user in users:
#     print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user.get('email', 'N/A')}")

