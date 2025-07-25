import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

MOODLE_URL= os.getenv("MOODLE_URL")
TOKEN  = os.getenv("TOKEN")
COURSE_ID = 2       # Replace with your actual course ID
USER_ID = 438      # Replace with the student’s user ID

# --- API Endpoint ---
REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"


# params = {
#     'wstoken': TOKEN,
#     'wsfunction': 'gradereport_user_get_grade_items',
#     'moodlewsrestformat': 'json',
#     'courseid': COURSE_ID,
#     'userid': USER_ID        # Replace with course ID
# }

# response = requests.post(REST_URL, params=params)
# data = response.json()

# print("Grade items for user:", data)

# --- Parameters ---
params = {
    'wstoken': TOKEN,
    'wsfunction': 'gradereport_user_get_grade_items',
    'moodlewsrestformat': 'json',
    'courseid': COURSE_ID,
    'userid': USER_ID
}

# --- API Request ---
response = requests.get(REST_URL, params=params)
data = response.json()

# --- Output Result ---
print(json.dumps(data, indent=2, ensure_ascii=False))

# --- Optional: Print Grades Only ---
if 'usergrades' in data and len(data['usergrades']) > 0:
    user_grade = data['usergrades'][0]
    print(f"\nGrades for: {user_grade['userfullname']} (User ID: {USER_ID})")
    for item in user_grade['gradeitems']:
        item_name = item.get('itemname')
        grade = item.get('gradeformatted')
        print(f"{item_name}: {grade}")
else:
    print("No grades found or invalid user/course ID.")
