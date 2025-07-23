import os
import sys
import pandas as pd

# Setup path
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.split(curr_dir)[0]))
sys.path.append(os.path.dirname(curr_dir))

# Import functions
from moodle.function_name.get_course_assign import get_moodle_assignments
from moodle.function_name.get_assign_submission import get_assignment_submissions
from nudges.submission_nudges.submission_time_function import *
from threshold.all_threshold import return_userid_sub_threshold

def main(token, course_id, moodle_url, assignment_id):
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
    print("Assignment Due Date + Submissions:")
    print(df_assign_due_sub)

    # Calculate time and score
    moodle_sub_score = moodle_calculate_time_and_score(df_assign_due_sub, T_max=14, T_late=-2)
    print("Submission Time + Score:")
    print(moodle_sub_score)

    # Summary of early/late
    df_summary_early_late = moodle_sum_early_late_counts(moodle_sub_score)
    print("Summary of Early/Late Submissions:")
    print(df_summary_early_late)

    # Get users below threshold
    tigger_sub_userid = return_userid_sub_threshold(moodle_sub_score, sub_threshold=0.02)
    print("Triggered Users (Below Threshold):")
    print(tigger_sub_userid)

    # ✅ Return user IDs and assignment/course info
    return tigger_sub_userid, course_id, assignment_id

if __name__ == "__main__":
    # Define input parameters
    TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
    COURSE_ID = 2
    MOODLE_URL = "https://moodle.c3l.ai"
    ASSIGNMENT_ID = 1

    # Call main
    triggered_users, course_id, assignment_id = main(TOKEN, COURSE_ID, MOODLE_URL, ASSIGNMENT_ID)

    print("\nReturned from main():")
    print("Course ID:", course_id)
    print("Assignment ID:", assignment_id)
    print("Triggered User IDs:", triggered_users)


# import os
# import sys

# curr_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(os.path.split(curr_dir)[0]))
# sys.path.append(os.path.dirname(curr_dir))

# from moodle.function_name.get_course_assign import *
# from moodle.function_name.get_assign_submission import *
# from nudges.submission_nudges.submission_time_function import *
# from threshold.all_threshold import *

# # Set your token and course ID
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# COURSE_ID = 2
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# ASSIGNMENT_ID = 1 


# assignments = get_moodle_assignments(COURSE_ID, TOKEN)



# assignment_id = [
#     assignment for assignment in assignments["Testing_EngageAI"]
#     if assignment["assignment_id"] == 1
# ]


# # Convert list of assignments to a DataFrame
# df_assign_duedate = pd.DataFrame(assignment_id)
# df_submissions = get_assignment_submissions(MOODLE_URL, TOKEN, ASSIGNMENT_ID)

# df_assign_due_sub=moodle_attach_assign_duedate(df_assign_duedate, df_submissions)
# print(df_assign_due_sub)

# moodle_sub_score=moodle_calculate_time_and_score(df_assign_due_sub, T_max=14, T_late=-2)
# print(moodle_sub_score)

# df_summary_early_late = moodle_sum_early_late_counts(moodle_sub_score)
# print(df_summary_early_late)

# tigger_sub_uerid=return_userid_sub_threshold(moodle_sub_score, sub_threshold=0.02)
# print(tigger_sub_uerid)