import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.readcsv_writehtml import read_csv_s3, write_html, add_section, save_html_s3, convert_to_datetime
from src.service.video import VideoService


######## Config ########
bucket = "engage-ai-raw-dataset"
start = "14/07/2025"
end = "21/07/2025"
file_video_name = "engageai_weekly_assessment/testing_video_SP1_Panopto.csv"

######## Read CSV File ########
df_video = read_csv_s3(bucket, file_video_name)
df_video = convert_to_datetime(column_name="Timestamp", df=df_video, tz="Australia/Adelaide")
print(df_video.columns)

######## Service ########
service = VideoService("df_video")
df_video = service.need_columns(df_video)
print(df_video)
print(df_video.columns)
print(df_video['Timestamp'].min())
print(df_video['Timestamp'].max())

# df_duedate = service.convert_to_datetime("duedate", df=df_duedate, tz="Australia/Adelaide")
# df_duedate = service.get_latest_due_date(df=df_duedate)
# df_duedate = df_duedate.sort_values(['duedate', 'cmid']).reset_index(drop=True)

# df_log = service.log_to_action_time(df_log)
# week_log = service.filter_actions_by_period(df_log, col_name="time", start=start, end=end)
# df_sub_log = service.get_action_submit(week_log, start=start, end=end)
