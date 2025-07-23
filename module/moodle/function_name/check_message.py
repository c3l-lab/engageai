import requests

def get_messages(moodle_url, token, userid_from, userid_to):
    url = f"{moodle_url}/webservice/rest/server.php"

    params = {
        "wstoken": token,
        "wsfunction": "core_message_get_messages",
        "moodlewsrestformat": "json"
    }

    data = {
        "useridto": userid_to,
        "useridfrom": userid_from,
        "type": "both",  # options: 'conversations', 'notifications', 'both'
        "read": 0,       # 0 = unread, 1 = read
        "newestfirst": 1,
        "limitfrom": 0,
        "limitnum": 20
    }

    response = requests.post(url, params=params, data=data)

    if response.status_code == 200:
        messages = response.json().get("messages", [])
        for msg in messages:
            print(f"[{msg['timecreated']}] {msg['text']}")
        return messages
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


# Example usage:
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"

# Assuming you already have the sender (admin or teacher) and recipient user IDs
SENDER_ID = 2
RECIPIENT_ID = 438
# RECIPIENT_ID = 438

check=get_messages(MOODLE_URL, TOKEN, SENDER_ID, RECIPIENT_ID)
check