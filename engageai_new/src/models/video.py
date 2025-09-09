from pydantic import BaseModel
from datetime import datetime

class Video(BaseModel):
    student_id: str
    video_minutes_watched: float

    timestamp: datetime
    folder_name: str
    folder_id: str
    session_name: str
    session_id: str
    minutes_delivered: float
    username: str
    user_id: str
    name: str
    email: str
    viewing_type: str
    root_folder_level0: str
    subfolder_level1: str
    subfolder_level2: str
