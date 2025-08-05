import requests
from datetime import datetime

def get_moodle_assignments(course_id, token, moodle_url="https://moodle.c3l.ai"):
 
    function_name = "mod_assign_get_assignments"
    rest_url = f"{moodle_url}/webservice/rest/server.php"

    params = {
        "wstoken": token,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
        "courseids[0]": course_id
    }

    response = requests.get(rest_url, params=params)
    data = response.json()

    result = {}

    if "courses" in data:
        for course in data["courses"]:
            course_name = course.get("fullname", "Unnamed Course")
            result[course_name] = []
            for assignment in course.get("assignments", []):
                assignment_id = assignment.get("id", "N/A")
                name = assignment.get("name", "No name")
                duedate_unix = assignment.get("duedate", 0)
                duedate = datetime.fromtimestamp(duedate_unix).strftime('%Y-%m-%d %H:%M:%S') if duedate_unix else "No due date"
                
                result[course_name].append({
                    "assignment_id": assignment_id,
                    "name": name,
                    "due_date": duedate
                })
    else:
        result["error"] = data

    return result

# # Set your token and course ID
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# COURSE_ID = 2

# assignments = get_moodle_assignments(COURSE_ID, TOKEN)
# print(assignments)


