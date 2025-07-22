import requests
import json

def get_moodle_users(moodle_url, token, function="core_user_get_users", search_query="%"):

    url = f"{moodle_url}/webservice/rest/server.php"

    params = {
        "wstoken": token,
        "wsfunction": function,
        "moodlewsrestformat": "json"
    }

    data = {
        "criteria[0][key]": "firstname",
        "criteria[0][value]": search_query,
    }

    response = requests.post(url, params=params, data=data)

    if response.status_code == 200:
        result = response.json()
        return result.get("users", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Example usage
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
users = get_moodle_users(MOODLE_URL, TOKEN)

for user in users:
    print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user['email']}")


# # SUCCESSFUL AND FROM HAIYUE
# import requests
# import json
# # Replace these with your values
# MOODLE_URL = "https://moodle.c3l.ai"
# # TOKEN = "4ba3fd94d4276b536e2958c7a575e00b"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# FUNCTION = "core_user_get_users"
# SEARCH_QUERY = "%"  # or leave empty to get all users (limited result)

# # Build the URL
# url = f"{MOODLE_URL}/webservice/rest/server.php"

# # Parameters for the function
# params = {
#     "wstoken": TOKEN,
#     "wsfunction": FUNCTION,
#     "moodlewsrestformat": "json"
#     }

# data = {
#     "criteria[0][key]": "firstname",   # or "email", "username", etc.
#     "criteria[0][value]": SEARCH_QUERY,
# }
# print(json.dumps(params))

# # Send the request
# response = requests.post(url, params=params, data=data)

# # Parse the result
# if response.status_code == 200:
#     users = response.json().get("users", [])
#     print(users)
#     for user in users:
#         print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user['email']}")
# else:
#     print(f"Error: {response.status_code} - {response.text}")
