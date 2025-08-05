import requests
import os
import sys

curr_dir=os.path.abspath(__file__)
sys.path.append(os.path.split(curr_dir)[0])
from get_user import *

import requests

def send_message_to_user(moodle_url, token, to_user_id, message_text):
    url = f"{moodle_url}/webservice/rest/server.php"
    
    params = {
        "wstoken": token,
        "wsfunction": "core_message_send_instant_messages",
        "moodlewsrestformat": "json"
    }

    # ✅ Required fields only — NO empty strings!
    data = {
        "messages[0][touserid]": to_user_id,
        "messages[0][text]": message_text,
        "messages[0][textformat]": 1,  # 1 = HTML format
    }

    response = requests.post(url, params=params, data=data)

    if response.status_code == 200:
        print("✅ Message sent successfully:")
        print(response.json())
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


# Example usage:
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
user_id = 438
print(f"Sending to user ID: {user_id}")
send_message_to_user(MOODLE_URL, TOKEN, user_id, "Hello from fixed Moodle API script!")


