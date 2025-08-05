import requests
import random
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

MOODLE_URL = os.getenv("MOODLE_URL")  # e.g., https://moodle.c3l.ai
TOKEN = os.getenv("TOKEN")            # Your web service token
COURSE_ID = 2                         # Your course ID

REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"


def call_moodle_api(function_name, parameters):
    parameters.update({
        'wstoken': TOKEN,
        'moodlewsrestformat': 'json',
        'wsfunction': function_name
    })
    response = requests.post(REST_URL, data=parameters)
    response.raise_for_status()
    return response.json()


# ✅ Step 1: Get Enrolled Users
def get_enrolled_users(course_id):
    users = call_moodle_api('core_enrol_get_enrolled_users', {'courseid': course_id})
    # Only students (adjust if your roles differ)
    students = [u for u in users if any(role['shortname'] == 'student' for role in u['roles'])]
    return students


# ✅ Step 2: Get All Assignments and Their ContextIDs
def get_assignments_with_context(course_id):
    content = call_moodle_api('core_course_get_contents', {'courseid': course_id})
    assignments = []
    for section in content:
        for mod in section.get('modules', []):
            if mod['modname'] == 'assign':
                assignments.append({
                    'name': mod['name'],
                    'id': mod['instance'],      # assignment instance ID
                    'contextid': mod['contextid']
                })
    return assignments


# ✅ Step 3: Submit Fake Grades using `core_grades_grader_gradingpanel_point_store`
def submit_fake_grades(assignments, students):
    for assign in assignments:
        print(f"\n🎯 Assignment: {assign['name']} (ID: {assign['id']}, ContextID: {assign['contextid']})")
        for student in students:
            fake_grade = round(random.uniform(60, 100), 2)

            print(f" → Submitting {fake_grade} for {student['fullname']} (User ID: {student['id']})")

            params = {
                'component': 'mod_assign',
                'contextid': assign['contextid'],
                'itemname': 'submission',
                'gradeduserid': student['id'],
                'grade': fake_grade,
                'scaleid': ''  # leave blank if not using scale
            }

            try:
                result = call_moodle_api('core_grades_grader_gradingpanel_point_store', params)
                if result == {}:
                    print("    ✅ Grade submitted successfully")
                else:
                    print(f"    ⚠️ Unexpected response: {result}")
            except Exception as e:
                print(f"    ❌ Error submitting grade: {e}")


# ✅ MAIN EXECUTION
if __name__ == '__main__':
    students = get_enrolled_users(COURSE_ID)
    print(f"📚 Found {len(students)} students.")

    assignments = get_assignments_with_context(COURSE_ID)
    print(f"📝 Found {len(assignments)} assignments.")

    submit_fake_grades(assignments, students)

    print("\n✅ All grades submitted.")



# import requests
# import random
# import os
# from dotenv import load_dotenv

# load_dotenv()


# MOODLE_URL = os.getenv("MOODLE_URL")
# TOKEN = os.getenv("TOKEN")
# COURSE_ID = 2  # Replace with your course ID

# REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"


# def call_moodle_api(function_name, parameters):
#     parameters.update({
#         'wstoken': TOKEN,
#         'moodlewsrestformat': 'json',
#         'wsfunction': function_name
#     })
#     response = requests.post(REST_URL, data=parameters)
#     response.raise_for_status()
#     return response.json()


# # Step 1: Get enrolled users in the course
# def get_enrolled_users(course_id):
#     return  print( call_moodle_api('core_enrol_get_enrolled_users', {'courseid': course_id}))

# ######### get the context_id ########################

# # params = {
# #     'wstoken': TOKEN,
# #     'wsfunction': 'core_course_get_contents',
# #     'moodlewsrestformat': 'json',
# #     'courseid': COURSE_ID  # Replace with your course ID
# # }

# # response = requests.post(REST_URL, params=params)
# # modules = response.json()

# # # Display module names and contextids
# # for section in modules:
# #     for mod in section.get('modules', []):
# #         print(f"Name: {mod['name']}, ID: {mod['id']}, modname: {mod['modname']}, contextid: {mod['contextid']}")

# ########## get the context_id ########################


# # Step 2: Get all assignments in the course
# def get_assignments(course_id):
#     data = call_moodle_api('mod_assign_get_assignments', {'courseids[0]': course_id})
#     assignments = []
#     for course in data['courses']:
#         for assign in course['assignments']:
#             assignments.append({
#                 'id': assign['id'],
#                 'name': assign['name'],
#                 'cmid': assign['cmid']
#             })
#     return print(assignments)


# # Step 3: Update grades for all users and assignments
# def fake_grades(course_id, users, assignments):
#     for assign in assignments:
#         print(f"\nFaking grades for assignment: {assign['name']} (Assign ID: {assign['id']}, cmid: {assign['cmid']})")

#         for user in users:
#             fake_score = round(random.uniform(60.0, 100.0), 2)
#             print(f"  User: {user['fullname']} (ID: {user['id']}) → Grade: {fake_score}")

#             grade_data = {
#                 'gradeupdates[0][itemtype]': 'mod',
#                 'gradeupdates[0][itemmodule]': 'assign',
#                 'gradeupdates[0][iteminstance]': assign['id'],
#                 'gradeupdates[0][grades][0][userid]': user['id'],
#                 'gradeupdates[0][grades][0][grade]': fake_score
#             }

#             result = call_moodle_api('core_grade_update_grades', grade_data)

#             if 'warnings' in result and result['warnings']:
#                 print(f"  ⚠️ Warning: {result['warnings']}")
#             else:
#                 print("  ✅ Grade submitted successfully")

# # ---- Run All Steps ----
# enrolled_users = get_enrolled_users(COURSE_ID)
# assignments = get_assignments(COURSE_ID)
# fake_grades(COURSE_ID, enrolled_users, assignments)


# # import requests
# # import json
# # import random
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # # --- Config ---
# # MOODLE_URL = os.getenv("MOODLE_URL")
# # TOKEN =os.getenv("TOKEN")
# # COURSE_ID = 2

# # REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# # # Step 1: Get assignments in the course
# # def get_assignments():
# #     params = {
# #         'wstoken': TOKEN,
# #         'wsfunction': 'mod_assign_get_assignments',
# #         'moodlewsrestformat': 'json'
# #     }
# #     response = requests.get(REST_URL, params=params)
# #     data = response.json()
# #     course_assigns = []
# #     for course in data['courses']:
# #         if course['id'] == COURSE_ID:
# #             for assign in course['assignments']:
# #                 course_assigns.append({
# #                     'id': assign['id'],
# #                     'name': assign['name']
# #                 })
# #     return course_assigns

# # # Step 2: Get enrolled users (students)
# # def get_enrolled_users():
# #     params = {
# #         'wstoken': TOKEN,
# #         'wsfunction': 'core_enrol_get_enrolled_users',
# #         'moodlewsrestformat': 'json',
# #         'courseid': COURSE_ID
# #     }
# #     response = requests.get(REST_URL, params=params)
# #     users = response.json()
# #     # Filter students only (roles may vary, adjust if needed)
# #     students = [u for u in users if any(role['shortname'] == 'student' for role in u['roles'])]
# #     return students

# # # Step 3: Submit fake grades
# # def submit_grade(assign_id, user_id, grade):
# #     data = {
# #         'wstoken': TOKEN,
# #         'wsfunction': 'core_grade_update_grades',
# #         'moodlewsrestformat': 'json',
# #         'gradeupdates[0][itemtype]': 'mod',
# #         'gradeupdates[0][itemmodule]': 'assign',
# #         'gradeupdates[0][iteminstance]': assign_id,
# #         'gradeupdates[0][grades][0][userid]': user_id,
# #         'gradeupdates[0][grades][0][grade]': grade
# #     }
# #     response = requests.post(REST_URL, data=data)
# #     return response.json()

# # # Run the whole process
# # assignments = get_assignments()
# # students = get_enrolled_users()

# # print(f"Found {len(assignments)} assignments and {len(students)} students.\n")

# # for assign in assignments:
# #     print(f"📘 Assignment: {assign['name']} (ID: {assign['id']})")
# #     for student in students:
# #         fake_grade = round(random.uniform(60, 100), 2)  # Fake grade between 60–100
# #         result = submit_grade(assign['id'], student['id'], fake_grade)
# #         print(f" → Grade {fake_grade} submitted for {student['fullname']} (ID: {student['id']})")

# # print("\n✅ Grade submission complete.")
