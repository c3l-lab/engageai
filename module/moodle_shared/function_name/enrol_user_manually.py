# enroll_half_users.py
import requests
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_user import *

MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
ENROL_FUNCTION = "enrol_manual_enrol_users"
COURSE_ID = 2  # Target course
ROLE_ID = 5    # Usually 5 = student

def enroll_users(user_ids):
    url = f"{MOODLE_URL}/webservice/rest/server.php"
    params = {
        "wstoken": TOKEN,
        "wsfunction": ENROL_FUNCTION,
        "moodlewsrestformat": "json"
    }
    
    enrolments = {}
    for idx, user_id in enumerate(user_ids):
        enrolments[f'enrolments[{idx}][roleid]'] = ROLE_ID
        enrolments[f'enrolments[{idx}][userid]'] = user_id
        enrolments[f'enrolments[{idx}][courseid]'] = COURSE_ID

    response = requests.post(url, params=params, data=enrolments)
    if response.status_code == 200:
        print("Users successfully enrolled.")
    else:
        print(f"Enrollment failed: {response.status_code}, {response.text}")

# Get users and split in half
users = get_moodle_users(MOODLE_URL, TOKEN)
user_ids = [user['id'] for user in users]
half_count = len(user_ids) // 2
first_half = user_ids[:half_count]

# Enroll first half
enroll_users(first_half)
