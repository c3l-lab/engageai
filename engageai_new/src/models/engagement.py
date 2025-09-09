from pydantic import BaseModel


class Engagement(BaseModel):
    student_id: str
    login_count: int
    forum_posts: int
    video_minutes_watched: float


    