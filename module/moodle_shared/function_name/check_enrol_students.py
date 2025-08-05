import requests

def get_enrolled_users(moodle_url, token, course_id):

    url = f"{moodle_url}/webservice/rest/server.php"

    params = {
        "wstoken": token,
        "wsfunction": "core_enrol_get_enrolled_users",
        "moodlewsrestformat": "json"
    }

    data = {
        "courseid": course_id
    }

    response = requests.post(url, params=params, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# # Example usage
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# COURSE_ID = 2

# enrolled_users = get_enrolled_users(MOODLE_URL, TOKEN, COURSE_ID)

# for user in enrolled_users:
#     print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user.get('email', 'N/A')}")
