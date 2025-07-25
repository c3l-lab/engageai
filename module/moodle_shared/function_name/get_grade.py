import requests
from dotenv import load_dotenv
import os

load_dotenv()

MOODLE_URL= os.getenv("MOODLE_URL")
TOKEN  = os.getenv("TOKEN")
COURSE_ID = 2  # Replace with your actual course ID

# API endpoint
REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# API parameters
params = {
    'wstoken': TOKEN,
    'wsfunction': 'gradereport_user_get_grade_items',
    'moodlewsrestformat': 'json',
    'courseid': COURSE_ID
}

# Send request
response = requests.get(REST_URL, params=params)
data = response.json()

# Output response
import json
print(json.dumps(data, indent=2, ensure_ascii=False))
