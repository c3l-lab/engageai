from pydantic import BaseModel


class Nudge(BaseModel):
    moodle_url: str
    token: str
    course_id: int
    student_id: str
    message: str



# for user_id in triggered_users_id:
#     print(f"📨 Sending to user ID: {user_id}")
#     send_message_to_user(MOODLE_URL, TOKEN, user_id, "📢 Hello! This is a reminder based on your submission index score.")
