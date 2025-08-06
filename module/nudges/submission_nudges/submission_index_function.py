import os
import sys
import pandas as pd

# Setup path
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.split(curr_dir)[0]))
sys.path.append(os.path.dirname(curr_dir))

# Import functions
from moodle_shared.function_name.get_course_assign import get_moodle_assignments
from moodle_shared.function_name.check_enrol_students import get_enrolled_users
from moodle_shared.function_name.get_assign_submission import get_assignment_submissions
from moodle_shared.function_name.sent_message import send_message_to_user
from nudges.submission_nudges.submission_function import *
from threshold.all_threshold import return_userid_sub_threshold


################## generate_submission_index_trigger_users ########################################################

def generate_submission_index_trigger_users(token, course_id, moodle_url, assignment_id):
    # Get assignments
    assignments = get_moodle_assignments(course_id, token)

    # Filter assignment by ID
    assignment_info = [
        assignment for assignment in assignments.get("Testing_EngageAI", [])
        if assignment.get("assignment_id") == assignment_id
    ]

    # Convert to DataFrame
    df_assign_duedate = pd.DataFrame(assignment_info)

    # Get submissions
    df_submissions = get_assignment_submissions(moodle_url, token, assignment_id)

    # Attach due date info
    df_assign_due_sub = moodle_attach_assign_duedate(df_assign_duedate, df_submissions)

    # Calculate time and score
    moodle_sub_score = moodle_calculate_time_and_score(df_assign_due_sub, T_max=14, T_late=-2)

    # Summary of early/late
    df_summary_early_late = moodle_sum_early_late_counts(moodle_sub_score)

    # Get users below threshold
    tigger_sub_userid = return_userid_sub_threshold(moodle_sub_score, sub_threshold=0.02)

    # ✅ Return user IDs and assignment/course info
    return tigger_sub_userid, course_id, assignment_id


################## submission reminder whole preocess  ########################################################


# def submission_reminder_time(token, course_id, moodle_url,days_before_due=14):



#     assignments = get_moodle_assignments(course_id, token)
#     pre_duedate_assign=process_duedate_reminder(assignments, days_before_due=14)
#     print(pre_duedate_assign)

#     enrolled_users = get_enrolled_users(moodle_url,token, course_id)

#     for user in enrolled_users:
#         print(f"ID: {user['id']}, Name: {user['fullname']}, Email: {user.get('email', 'N/A')}")


#     return assignments

def submission_reminder_time(token, course_id, moodle_url, days_before_due=14):
    today_str = datetime.today().strftime('%Y-%m-%d')
    print(f"📅 Today is: {today_str}")
    
    # Get assignments and enrolled users
    assignments = get_moodle_assignments(course_id, token)
    print("📘 Assignments:", assignments)
    
    users = get_enrolled_users(moodle_url, token, course_id)
    print("👥 Enrolled Users:", users)
    
    pre_duedate_assign = process_duedate_reminder(assignments, days_before_due=days_before_due)
    print("📌 Pre-due-date Assignments:", pre_duedate_assign)

    today_reminders = []

    for course_name, assignment_list in pre_duedate_assign.items():
        for assign in assignment_list:
            pre_date = assign.get("pre_reminder_date", "").split(" ")[0]  # Strip time
            if pre_date == today_str:
                today_reminders.append(assign)

    for reminder in today_reminders:
        name = reminder['name']
        due_date = reminder['due_date'].split(" ")[0]

        message = (
            f"<p>Reminder: The assignment <strong>{name}</strong> is due on <strong>{due_date}</strong>, "
            f"which is 14 days from now. Please start early to avoid missing the deadline. "
            f"If you have any questions, don't hesitate to ask in the course forum.</p>"
        )

        print(f"📢 Sending reminder for: {name}")

        for user in users:
            user_id = user.get('id')
            if user_id:
                send_message_to_user(moodle_url, token, user_id, message)

    return today_reminders