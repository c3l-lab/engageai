import pandas as pd
from src.models import video

class VideoService:
    def __init__(self, VideoPanopto: pd.DataFrame= None):
        self.student_id: str
        self.video_minutes_watched: float
        self.timestamp: pd.datetime
        self.folder_name: str
        self.folder_id: str
        self.session_name: str
        self.session_id: str
        self.minutes_delivered: float
        self.username: str
        self.user_id: str
        self.name: str
        self.email: str
        self.viewing_type: str
        self.root_folder_level0: str
        self.subfolder_level1: str
        self.subfolder_level2: str


    ######### needed columns ##############################################################################
    def need_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        needed_columns = [
    #     'Timestamp','Folder ID', 'Session Name', 'Session ID',
    #    'Minutes Delivered', 'UserName', 'User ID', 'Name', 'Email',
    #    'Viewing Type'

    'Timestamp','Session Name', 'Session ID',
       'Minutes Delivered', 'UserName', 'User ID'
        ]
        df = df[needed_columns]
        return df