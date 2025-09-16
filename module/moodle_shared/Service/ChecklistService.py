import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Moodle API Configuration
MOODLE_URL = os.getenv("MOODLE_URL").rstrip("/")
TOKEN = os.getenv("Checklist_TOKEN")
COURSE_ID = 2    # Replace with your actual course ID
USER_ID = 438     # Replace with your student's user ID

# -------------------------------------------
# Step 1: Get Activity Completion Status
# -------------------------------------------
completion_params = {
    'wstoken': TOKEN,
    'wsfunction': 'core_completion_get_activities_completion_status',
    'moodlewsrestformat': 'json',
    'courseid': COURSE_ID,
    'userid': USER_ID
}

completion_response = requests.get(
    f"{MOODLE_URL}/webservice/rest/server.php",
    params=completion_params
)

completion_data = completion_response.json()

if 'exception' in completion_data:
    print("Error fetching activity completion:", completion_data)
    exit()

# -------------------------------------------
# Step 2: Get Course Modules to Map cmid to Name
# -------------------------------------------
contents_params = {
    'wstoken': TOKEN,
    'wsfunction': 'core_course_get_contents',
    'moodlewsrestformat': 'json',
    'courseid': COURSE_ID
}

contents_response = requests.get(
    f"{MOODLE_URL}/webservice/rest/server.php",
    params=contents_params
)

contents_data = contents_response.json()
print(contents_data)

# Build cmid-to-name dictionary
cmid_to_name = {}
for section in contents_data:
    for mod in section.get('modules', []):
        cmid_to_name[mod['id']] = mod.get('name', f"Unnamed Module ({mod['id']})")

print(cmid_to_name)
# -------------------------------------------
# Step 3: Display Completion Report
# -------------------------------------------
print(f"\n📋 Completion Report for User ID {USER_ID} in Course ID {COURSE_ID}\n")

for activity in completion_data.get('statuses', []):
    cmid = activity.get('cmid')
    name = cmid_to_name.get(cmid, f"Activity ID {cmid}")
    completed = activity.get('state') == 1
    state_text = "✅ Completed" if completed else "❌ Not Completed"
    print(f"{name:<40} {state_text}")
    print(activity)


# import requests
# from dotenv import load_dotenv
# import os

# # Load variables from .env
# load_dotenv()
# # Config

# MOODLE_URL= os.getenv("MOODLE_URL")
# TOKEN  = os.getenv("Checklist_TOKEN")
# COURSE_ID = 2 # your course ID
# USER_ID = 438   # student user ID

# # API endpoint and parameters
# params = {
#     'wstoken': TOKEN,
#     'wsfunction': 'core_completion_get_activities_completion_status',
#     'moodlewsrestformat': 'json',
#     'courseid': COURSE_ID,
#     'userid': USER_ID
# }

# # response = requests.get(f"{MOODLE_URL}/webservice/rest/server.php", params=params)

# # # Show results
# # data = response.json()

# # for activity in data.get('statuses', []):
# #     print(activity)  # Debug line

# params = {
#     'wstoken': TOKEN,
#     'wsfunction': 'core_course_get_contents',
#     'moodlewsrestformat': 'json',
#     'courseid': COURSE_ID
# }

# response = requests.get(f"{MOODLE_URL}/webservice/rest/server.php", params=params)
# course_data = response.json()

# # Flatten modules to find cmid -> name
# cmid_to_name = {}
# for section in course_data:
#     for mod in section.get('modules', []):
#         cmid_to_name[mod['id']] = mod['name']

# # Print completion status with names
# for activity in data.get('statuses', []):
#     cmid = activity['cmid']
#     name = cmid_to_name.get(cmid, f"Activity {cmid}")
#     completed = activity['state'] == 1
#     print(f"{name}: {'✅ Completed' if completed else '❌ Not Completed'}")
