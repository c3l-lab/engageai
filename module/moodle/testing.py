# # testing.py
# from moodle import MoodleDataService  # replace 'your_module_name' with your python file name without `.py`
# import requests
# import pandas as pd
# from dotenv import load_dotenv
# import os

# # Load the .env file
# load_dotenv()

# MOODLE_URL = "https://moodle.c3l.ai/"
# # WEB_SERVICE_TOKEN = "your-token-here"
# WEB_SERVICE_TOKEN = os.getenv("TOKEN")

# print(WEB_SERVICE_TOKEN)

# def main():
#     # Create an instance of the MoodleDataService
#     moodle_service = MoodleDataService(MOODLE_URL, WEB_SERVICE_TOKEN)
    
#     users = moodle_service.get_all_users()

#     if users and 'users' in users:
#         for u in users['users']:
#             print(f"{u['id']}: {u['firstname']} {u['lastname']} ({u['email']})")
#     else:
#         print("No users returned.")


# if __name__ == "__main__":
#     main()



# SUCCESSFUL AND FROM HAIYUE
import requests

# Replace these with your values
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "4ba3fd94d4276b536e2958c7a575e00b"
FUNCTION = "core_user_get_users"
SEARCH_QUERY = "%"  # or leave empty to get all users (limited result)

# Build the URL
url = f"{MOODLE_URL}/webservice/rest/server.php"

# Parameters for the function
params = {
    "wstoken": TOKEN,
    "wsfunction": FUNCTION,
    "moodlewsrestformat": "json",
    "criteria[0][key]": "d",   # or "email", "username", etc.
    "criteria[0][value]": SEARCH_QUERY,
}

# Send the request
response = requests.get(url, params=params)

# Parse the result
if response.status_code == 200:
    users = response.json().get("users", [])
    print(users)
    for user in users:
        print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user['email']}")
else:
    print(f"Error: {response.status_code} - {response.text}")


# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()
# token = os.getenv("TOKEN")  # Or just paste token as a string
# url = "https://moodle.c3l.ai/webservice/rest/server.php"

# payload = {
#     "wstoken": token,
#     "wsfunction": "core_user_view_user_profile",
#     "moodlewsrestformat": "json",
#     "criteria[0][key]": "username",       # or username, idnumber, etc.
#     "criteria[0][value]": "@"
# }

# response = requests.post(url, data=payload)
# data = response.json()

# # Pretty print result
# from pprint import pprint
# pprint(data)


# SUCCESSFUL 
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# token = os.getenv("TOKEN")  # Or set token directly as a string
# url = "https://moodle.c3l.ai/webservice/rest/server.php"

# params = {
#     "wstoken": token,
#     "wsfunction": "core_course_get_courses",
#     "moodlewsrestformat": "json"
# }

# response = requests.post(url, data=params)

# print(response.status_code)
# print(response.json())
