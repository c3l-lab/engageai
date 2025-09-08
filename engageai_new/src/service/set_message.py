from models import sent_message


######from our moodle enviornemnt 
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

