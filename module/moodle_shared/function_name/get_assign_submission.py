import requests
import pandas as pd
from datetime import datetime

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "N/A"

def get_assignment_submissions(moodle_url, token, assignment_id):

    url = f"{moodle_url}/webservice/rest/server.php"

    params = {
        'wstoken': token,
        'wsfunction': 'mod_assign_get_submissions',
        'moodlewsrestformat': 'json'
    }

    data = {
        'assignmentids[0]': assignment_id
    }

    response = requests.post(url, params=params, data=data)

    if response.status_code == 200:
        result = response.json()
        records = []

        if result.get("assignments"):
            for assignment in result['assignments']:
                for submission in assignment.get("submissions", []):
                    record = {
                        "userid": submission["userid"],
                        "status": submission["status"],
                        "timecreated": submission["timecreated"],
                        "timemodified": submission["timemodified"],
                        "timecreated_readable": format_time(submission["timecreated"]),
                        "timemodified_readable": format_time(submission["timemodified"]),
                    }
                    records.append(record)

        df = pd.DataFrame(records)
        return df
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return pd.DataFrame()

# === Example Usage ===
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
ASSIGNMENT_ID = 1  # Replace with your actual assignment ID

df_submissions = get_assignment_submissions(MOODLE_URL, TOKEN, ASSIGNMENT_ID)

# Print the resulting DataFrame
print(df_submissions)
<<<<<<< HEAD
=======


# import requests

# def get_assignment_submissions(moodle_url, token, assignment_id):
   
#     url = f"{moodle_url}/webservice/rest/server.php"

#     params = {
#         'wstoken': token,
#         'wsfunction': 'mod_assign_get_submissions',
#         'moodlewsrestformat': 'json'
#     }

#     data = {
#         'assignmentids[0]': assignment_id
#     }

#     response = requests.post(url, params=params, data=data)
#     if response.status_code == 200:
#         result = response.json()
#         submissions = []
#         if result.get("assignments"):
#             for assignment in result['assignments']:
#                 for submission in assignment.get("submissions", []):
#                     submissions.append({
#                         "userid": submission["userid"],
#                         "status": submission["status"],
#                         "timecreated": submission["timecreated"],
#                         "timemodified": submission["timemodified"]
#                     })
#         return submissions
#     else:
#         print(f"Error: {response.status_code} - {response.text}")
#         return []

# # === Example Usage ===
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# ASSIGNMENT_ID = 1  # Replace with actual assignment ID from the course

# submissions = get_assignment_submissions(MOODLE_URL, TOKEN, ASSIGNMENT_ID)

# # Display submission times
# from datetime import datetime

# def format_time(ts):
#     return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "N/A"

# for s in submissions:
#     print(f"User ID: {s['userid']} | Status: {s['status']} | Created: {format_time(s['timecreated'])} | Modified: {format_time(s['timemodified'])}")
>>>>>>> aws
