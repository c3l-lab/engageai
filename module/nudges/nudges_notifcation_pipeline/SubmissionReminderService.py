import os
import sys
import pandas as pd

# Setup paths
curr_dir = os.path.dirname(os.path.abspath(__file__))
pa_dir = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])

sys.path.append(os.path.abspath(os.path.split(curr_dir)[0]))
sys.path.append(os.path.abspath(os.path.split(pa_dir)[0]))

# # Import custom functions
# from moodle_shared.function_name.sent_message import *
# from moodle_shared.function_name.check_message import *
from submission_nudges.submission_index_function import submission_reminder_time


# Moodle API setup
TOKEN ="4ba3fd94d4276b536e2958c7a575e00b"
COURSE_ID = 2
MOODLE_URL = "https://moodle.c3l.ai"
# ASSIGNMENT_ID = 1
# SENDER_ID = 2  # The sender's user ID

reminder_service= submission_reminder_time(TOKEN, COURSE_ID, MOODLE_URL, days_before_due=14)
print(reminder_service)


# # print("#################################################################")
# # print("🔍 Checking message delivery:")

# # for user_id in triggered_users_id:
# #     print(f"📥 Checking messages for user ID: {user_id}")
# #     messages = get_messages(MOODLE_URL, TOKEN, SENDER_ID, user_id)
# #     print(messages)
