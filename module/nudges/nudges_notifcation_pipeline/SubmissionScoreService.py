import os
import sys
import pandas as pd

# Setup paths
curr_dir = os.path.dirname(os.path.abspath(__file__))
pa_dir = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])

sys.path.append(os.path.abspath(os.path.split(curr_dir)[0]))
sys.path.append(os.path.abspath(os.path.split(pa_dir)[0]))

# Import custom functions
from nudges.submission_nudges.submission_index_function import generate_submission_index_trigger_users
from moodle_shared.function_name.sent_message import *
from moodle_shared.function_name.check_message import *


# Moodle API setup
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
COURSE_ID = 2
MOODLE_URL = "https://moodle.c3l.ai"
ASSIGNMENT_ID = 1
SENDER_ID = 2  # The sender's user ID

# ✅ Call the main pipeline function
triggered_users_id, course_id, assignment_id = generate_submission_index_trigger_users(TOKEN, COURSE_ID, MOODLE_URL, ASSIGNMENT_ID)

print("#################################################################")
print("📩 Sending messages to users:")

for user_id in triggered_users_id:
    print(f"📨 Sending to user ID: {user_id}")
    send_message_to_user(MOODLE_URL, TOKEN, user_id, "📢 Hello! This is a reminder based on your submission index score.")

print("#################################################################")
print("🔍 Checking message delivery:")

for user_id in triggered_users_id:
    print(f"📥 Checking messages for user ID: {user_id}")
    messages = get_messages(MOODLE_URL, TOKEN, SENDER_ID, user_id)
    print(messages)



# Moodle API setup
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# COURSE_ID = 2
# MOODLE_URL = "https://moodle.c3l.ai"
# ASSIGNMENT_ID = 1
# SENDER_ID = 2  # The sender's user ID (admin/teacher)

# # Get list of users to send messages to
# # triggered_users_id, course_id, assignment_id = main(TOKEN, COURSE_ID, MOODLE_URL, ASSIGNMENT_ID)
# triggered_users_id, course_id, assignment_id = main()

# print("##########################################################################################################################################################")
# print("📩 Sending messages to users:")

# # ✅ Loop through each user in the list and send the message
# for user_id in triggered_users_id:
#     print(f"Sending to user ID: {user_id}")
#     send_message_to_user(MOODLE_URL, TOKEN, user_id, "📢 Hello! This is a reminder based on your submission index score.")

# print("##########################################################################################################################################################")
# print("📨 Checking if messages were received:")

# # ✅ Optionally check if the message appears in the recipient's inbox (via API)
# for user_id in triggered_users_id:
#     print(f"🔍 Checking messages for user ID: {user_id}")
#     messages = get_messages(MOODLE_URL, TOKEN, SENDER_ID, user_id)
#     print(messages)



