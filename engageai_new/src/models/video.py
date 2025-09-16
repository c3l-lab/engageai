from pydantic import BaseModel
from datetime import datetime

class Video(BaseModel):
    video_minutes_watched: float
    week: int
    timestamp: datetime
    session_name: str
    session_id: str
    minutes_delivered: float
    username: str
    user_id: str
    message: str

