import requests
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

class MoodleService:
    def __init__(self, moodle_url, token):
        self.moodle_url = moodle_url.rstrip("/")
        # self.token = token
        self.token =  token
        self.rest_url = f"{self.moodle_url}/webservice/rest/server.php"
        self.session = requests.Session()

    def _post(self, function, data=None):
        params = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json"
        }
        response = self.session.post(self.rest_url, params=params, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None

    def _get(self, function, data=None):
        params = {
            "wstoken": self.token,
            "wsfunction": function,
            "moodlewsrestformat": "json"
        }
        if data:
            params.update(data)
        response = self.session.get(self.rest_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None

    def get_users(self, search="%"):
        data = {
            "criteria[0][key]": "firstname",
            "criteria[0][value]": search
        }
        result = self._post("core_user_get_users", data)
        return result.get("users", []) if result else []

    def get_enrolled_users(self, course_id):
        return self._post("core_enrol_get_enrolled_users", {"courseid": course_id})

    def enroll_users(self, course_id, user_ids, role_id=5):
        data = {}
        for idx, uid in enumerate(user_ids):
            data[f'enrolments[{idx}][roleid]'] = role_id
            data[f'enrolments[{idx}][userid]'] = uid
            data[f'enrolments[{idx}][courseid]'] = course_id
        return self._post("enrol_manual_enrol_users", data)

    def get_assignments(self, course_id):
        result = self._get("mod_assign_get_assignments", {"courseids[0]": course_id})
        output = {}
        if result and "courses" in result:
            for course in result["courses"]:
                output[course["fullname"]] = []
                for a in course.get("assignments", []):
                    output[course["fullname"]].append({
                        "assignment_id": a["id"],
                        "name": a["name"],
                        "due_date": datetime.fromtimestamp(a["duedate"]).strftime("%Y-%m-%d %H:%M:%S") if a["duedate"] else "N/A"
                    })
        return output

    def get_assignment_submissions(self, assignment_id):
        result = self._post("mod_assign_get_submissions", {"assignmentids[0]": assignment_id})
        if result and result.get("assignments"):
            records = []
            for assignment in result["assignments"]:
                for s in assignment.get("submissions", []):
                    records.append({
                        "userid": s["userid"],
                        "status": s["status"],
                        "timecreated": s["timecreated"],
                        "timemodified": s["timemodified"],
                        "timecreated_readable": datetime.fromtimestamp(s["timecreated"]).strftime("%Y-%m-%d %H:%M:%S") if s["timecreated"] else "N/A",
                        "timemodified_readable": datetime.fromtimestamp(s["timemodified"]).strftime("%Y-%m-%d %H:%M:%S") if s["timemodified"] else "N/A",
                    })
            return pd.DataFrame(records)
        return pd.DataFrame()

    def send_message(self, to_user_id, message):
        data = {
            "messages[0][touserid]": to_user_id,
            "messages[0][text]": message,
            "messages[0][textformat]": 1
        }
        return self._post("core_message_send_instant_messages", data)

    def get_messages(self, userid_from, userid_to, limit=20):
        data = {
            "useridto": userid_to,
            "useridfrom": userid_from,
            "type": "both",
            "read": 0,
            "newestfirst": 1,
            "limitfrom": 0,
            "limitnum": limit
        }
        result = self._post("core_message_get_messages", data)
        return result.get("messages", []) if result else []

def main():
    
    MOODLE_URL= os.getenv("MOODLE_URL")
    TOKEN  = os.getenv("TOKEN")

    moodle = MoodleService(MOODLE_URL, TOKEN)  

if __name__ == "__main__":
    main()



# Class MoodleUser:
#      def __init__(self, moodle_url, token):
#         self.moodle_url = moodle_url.rstrip("/")
#         # self.token = token
#         self.token =  token
#         self.rest_url = f"{self.moodle_url}/webservice/rest/server.php"
#         self.session = requests.Session()
