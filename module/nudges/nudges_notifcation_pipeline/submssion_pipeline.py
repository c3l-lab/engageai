import os
import sys
import pandas as pd

# Setup paths
curr_dir = os.path.dirname(os.path.abspath(__file__))
pa_dir = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])

sys.path.append(os.path.abspath(os.path.split(curr_dir)[0]))
sys.path.append(os.path.abspath(os.path.split(pa_dir)[0]))

# Import custom functions
from submission_nudges.main import *
from moodle.function_name.sent_message import *
from moodle.function_name.check_message import *

# Moodle API setup
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
COURSE_ID = 2
MOODLE_URL = "https://moodle.c3l.ai"
ASSIGNMENT_ID = 1
SENDER_ID = 2  # The sender's user ID (admin/teacher)

# Get list of users to send messages to
triggered_users_id, course_id, assignment_id = main(TOKEN, COURSE_ID, MOODLE_URL, ASSIGNMENT_ID)

print("##########################################################################################################################################################")
print("📩 Sending messages to users:")

# ✅ Loop through each user in the list and send the message
for user_id in triggered_users_id:
    print(f"Sending to user ID: {user_id}")
    send_message_to_user(MOODLE_URL, TOKEN, user_id, "📢 Hello! This is a reminder based on your submission index score.")

print("##########################################################################################################################################################")
print("📨 Checking if messages were received:")

# ✅ Optionally check if the message appears in the recipient's inbox (via API)
for user_id in triggered_users_id:
    print(f"🔍 Checking messages for user ID: {user_id}")
    messages = get_messages(MOODLE_URL, TOKEN, SENDER_ID, user_id)
    print(messages)






# import os
# import sys
# import pandas as pd

# # Setup path
# curr_dir = os.path.dirname(os.path.abspath(__file__))
# pa_dir=os.path.dirname(os.path.split(os.path.abspath(__file__))[0])

# sys.path.append(os.path.abspath(os.path.split(curr_dir)[0]))
# sys.path.append(os.path.abspath(os.path.split(pa_dir)[0]))

# from submission_nudges.main import *
# from moodle.function_name.sent_message import *
# from moodle.function_name.check_message import *

# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# COURSE_ID = 2
# MOODLE_URL = "https://moodle.c3l.ai"
# ASSIGNMENT_ID = 1
# SENDER_ID = 2

# triggered_users_id, course_id, assignment_id = main(TOKEN, COURSE_ID, MOODLE_URL ,ASSIGNMENT_ID)

# print("##########################################################################################################################################################")
# print(f"Sending to user ID: {triggered_users_id}")
# send_message_to_user(MOODLE_URL, TOKEN, triggered_users_id, "Hello from fixed Moodle API script! Testing the sent message and based on the submssion index score")


# print("############################################################################################################################################")
# print(f"Checkinguser ID: {triggered_users_id} message received")
# get_messages(MOODLE_URL, TOKEN, SENDER_ID, triggered_users_id)

