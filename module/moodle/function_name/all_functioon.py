import requests
import json

class MoodleClient:
    def __init__(self, moodle_url, token):
        self.moodle_url = moodle_url.rstrip('/')
        self.token = token
        self.base_url = f"{self.moodle_url}/webservice/rest/server.php"

    def call_function(self, function_name, method='GET', params=None, data=None):
        payload = {
            "wstoken": self.token,
            "wsfunction": function_name,
            "moodlewsrestformat": "json"
        }

        if params:
            payload.update(params)

        if method == 'GET':
            response = requests.get(self.base_url, params=payload)
        elif method == 'POST':
            response = requests.post(self.base_url, params=payload, data=data)
        else:
            raise ValueError("Unsupported HTTP method.")

        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed request: {e}")
            print("Response Text:", response.text)
            return None

    def get_users_by_field(self, field, value):
        params = {
            "field": field,           # e.g., "email", "username", etc.
            "values[0]": value
        }
        return self.call_function("core_user_get_users_by_field", method='GET', params=params)

    def search_users(self, key="firstname", value="%"):
        data = {
            "criteria[0][key]": key,
            "criteria[0][value]": value
        }
        return self.call_function("core_user_get_users", method='POST', data=data)


# === Example Usage ===

# Replace with your actual Moodle URL and Token
client = MoodleClient("https://moodle.c3l.ai", "e2b64938f15b80d29e8845d4b54301e1")

# 🔹 Search users (with wildcard to list all)
users = client.search_users()
print("\n=== Search Results ===")
print(json.dumps(users, indent=2))

# 🔹 Get user by email
user_by_email = client.get_users_by_field("email", "paggie70424@gmail.com")
print("\n=== User By Email ===")
print(json.dumps(user_by_email, indent=2))
