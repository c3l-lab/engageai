# import requests
# from datetime import datetime

# # Moodle API Setup
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# FUNCTION_NAME = "mod_assign_get_assignments"
# REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# # Set course ID here (replace with real course ID)
# course_id = 2

# # Request parameters
# params = {
#     "wstoken": TOKEN,
#     "wsfunction": FUNCTION_NAME,
#     "moodlewsrestformat": "json"
# }

# # Send as GET with course ID list
# response = requests.get(REST_URL, params={**params, "courseids[0]": course_id})

# # Process response
# data = response.json()

# if "courses" in data:
#     for course in data["courses"]:
#         print(f"📘 Course: {course['fullname']}")
#         for assignment in course.get("assignments", []):
#             name = assignment["name"]
#             duedate_unix = assignment["duedate"]
#             duedate = datetime.fromtimestamp(duedate_unix).strftime('%Y-%m-%d %H:%M:%S') if duedate_unix else "No due date"
#             print(f"  📝 Assignment: {name}")
#             print(f"     📅 Due Date: {duedate}")
# else:
#     print("❌ Error or no assignments found:", data)

import requests
from datetime import datetime

# Moodle API Setup
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
FUNCTION_NAME = "mod_assign_get_assignments"
REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# Set course ID here (replace with real course ID)
course_id = 2

# Request parameters
params = {
    "wstoken": TOKEN,
    "wsfunction": FUNCTION_NAME,
    "moodlewsrestformat": "json"
}

# Send GET request with course ID list
response = requests.get(REST_URL, params={**params, "courseids[0]": course_id})

# Process response
data = response.json()

if "courses" in data:
    for course in data["courses"]:
        print(f"📘 Course: {course['fullname']}")
        for assignment in course.get("assignments", []):
            assignment_id = assignment.get("id", "N/A")  # Get assignment ID
            name = assignment.get("name", "No name")
            duedate_unix = assignment.get("duedate", 0)
            duedate = datetime.fromtimestamp(duedate_unix).strftime('%Y-%m-%d %H:%M:%S') if duedate_unix else "No due date"
            print(f"  📝 Assignment ID: {assignment_id}")
            print(f"     Name: {name}")
            print(f"     📅 Due Date: {duedate}")
else:
    print("❌ Error or no assignments found:", data)
