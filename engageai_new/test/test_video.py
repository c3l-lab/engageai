import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.readcsv_writehtml import (
    read_csv_s3, write_html, add_section, save_html_s3, convert_to_datetime
)
from src.service.video import VideoService


######## Config ########
bucket = "engage-ai-raw-dataset"
sem_start = "30-06-2025"
sem_end = "05-09-2025"

session_name='video_report'
week_start = "05-09-2025"
week_end = "12-09-2025"

file_weekvideo_name = "engageai_weekly_assessment/2025sp4_video_overview.csv"
file_statvideo_name = "engageai_weekly_assessment/EngageAI - video_duration.csv"
file_videolog_name = "engageai_weekly_assessment/testing_ViewsAndDownloads_20250905_09_12.csv"

######## Read CSV Files ########
df_statvideo_overview = read_csv_s3(bucket, file_statvideo_name)
df_weekvideo_overview = read_csv_s3(bucket, file_weekvideo_name)
df_video_log = read_csv_s3(bucket, file_videolog_name)
df_video_log = convert_to_datetime(column_name="Timestamp", df=df_video_log, tz="Australia/Adelaide")

######## Service ########
service = VideoService("df_video")

########## Define the week Period Date ################
week_th = service.define_whichweek(sem_start, sem_end, week_start, week_end)


df_statvideo_overview = service.need_statvideo_columns(df_statvideo_overview)
df_weekvideo_overview = service.need_weekvideo_columns(df_weekvideo_overview)
df_weekvideo_overview = service.fix_week_overview(df_weekvideo_overview)
df_weekvideo_duration = service.map_weekvideo_videoduration(df_statvideo_overview, df_weekvideo_overview)


##### There are overview of every week video in this semester ######
df_goupby_overview = service.groupby_week_overview(df_weekvideo_duration)

df_video_log = service.need_log_columns(df_video_log)
df_video_log = service.convert_to_mins(df_video_log)
df_summary = service.compute_per_video_stats(df_video_log)

per_user, per_user_video, per_user_session_summary = service.summary_per_user_videolog(df_summary)
####
with pd.option_context('display.max_columns', None,  # show all columns
                       'display.max_rows', None,     # show all rows
                       'display.max_colwidth', None, # show full column content
                       'display.width', 200):        # widen display
        # Print column names
    print(df_summary)
    print(per_user_session_summary)
###

week_video_summary = df_goupby_overview[df_goupby_overview['Week'] == week_th]
reminder_video_message = service.remind_week_videowatch(week_video_summary)

df_with_importance = service.video_weight_importance(df_weekvideo_duration)
df_user_video = service.map_weekvideo_duration_log(df_with_importance, per_user_video)
userid_video_percent = service.percentage_video_watch(df_user_video)
df_with_engagement = service.calculate_video_week_engagement(userid_video_percent)

nan_sessions = service.search_nan_session(df_with_engagement)

# Example manual edits
df_weekvideo_duration = service.edit_content_manually(
    df_weekvideo_duration,
    video_name='CURR 3021 W4 Evaluating Information BEYOND the CRAAP Test',
    week='W4',
    video_duration=5.14
)
df_weekvideo_duration = service.edit_content_manually(
    df_weekvideo_duration,
    video_name='CURR 3021 - 1 ePortfolio',
    week=1,
    video_duration=5.3
)

# Recompute after edit
df_with_importance = service.video_weight_importance(df_weekvideo_duration)
df_user_video = service.map_weekvideo_duration_log(df_with_importance, per_user_video)
userid_video_percent = service.percentage_video_watch(df_user_video)
df_with_engagement = service.calculate_user_engagement_indicator(userid_video_percent)

threshold = 0.3
reminder_df, triggered_ids = service.trigger_userid_sent_reminder(
    df_week_summary=week_video_summary,
    df_with_engagement=df_with_engagement,
    threshold=threshold
)


######## Build HTML Report ########
html_sections = []

add_section(html_sections, f"There are {len(df_weekvideo_overview)} unique videos in this course over the whole semester during semester Video Duration ({sem_start} to {sem_end})",
            df_weekvideo_duration.to_html(index=False, border=1))

add_section(html_sections, f"Weekly Video Overview (up to {week_end})",
            df_goupby_overview.to_html(index=False, border=1))

add_section(html_sections, "Video Importance based on the week video single video duration / total week video duration",
            df_with_importance .to_html(index=False, border=1))


add_section(html_sections, "Student Video Log)",
            df_video_log.head(50).to_html(index=False, border=1), include_dates=True,
            start=week_start, end=week_end)

add_section(html_sections, "Per-User Summary",
            per_user.head(50).to_html(index=False, border=1))

add_section(html_sections, "Per-User Video Summary",
            per_user_video.head(50).to_html(index=False, border=1))

add_section(html_sections, f"checking what is the per_user_session_video data look like after summary during {week_start} and {week_end}",
            per_user_session_summary.head(50).to_html(index=False, border=1))


add_section(html_sections, f"checking this week {week_th}th, there are unique {week_video_summary['Video_Count']} videos need to watch during {week_start} and {week_end}:",
            week_video_summary.head(50).to_html(index=False, border=1))


add_section(html_sections, "Video weight importance",
            df_with_importance.head(50).to_html(index=False, border=1))


add_section(html_sections, "student watch completion percentage",
            userid_video_percent.head(50).to_html(index=False, border=1))


add_section(html_sections, "Engagement Scores",
            df_with_engagement.head(50).to_html(index=False, border=1))


add_section(html_sections, f"There are {len(triggered_ids)} ppl need to be remineded",
            reminder_df.head(50).to_html(index=False, border=1))

# Save locally
html_content = write_html(html_sections, start=week_start, end=week_end)

######## Upload to S3 ########
save_html_s3(html_content, start=week_start, end=week_end, session_name=session_name)

# output_path = f"./output/video_report_{week_start}_{week_end}.html"
# os.makedirs(os.path.dirname(output_path), exist_ok=True)
# with open(output_path, "w", encoding="utf-8") as f:
#     f.write(html_report)

# Optional: upload to S3
# save_html_s3(html_report, bucket, "reports/video_report.html")

# print(f"✅ HTML report saved to {output_path}")
# print(f"Triggered reminders: {len(triggered_ids)} users -> {triggered_ids}")
