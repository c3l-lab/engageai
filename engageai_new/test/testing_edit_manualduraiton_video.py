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
sem_start="30-06-2025"
sem_end= "05-09-2025"

week_start="05-09-2025"
week_end= "12-09-2025"

file_weekvideo_name = "engageai_weekly_assessment/2025sp4_video_overview.csv"
file_statvideo_name = "engageai_weekly_assessment/EngageAI - video_duration.csv"
file_videolog_name = "engageai_weekly_assessment/testing_ViewsAndDownloads_20250905_09_12.csv"
# file_student_name= "engageai_weekly_assessment/panopto_studentid_to_userid.csv"

######## Read CSV File ########
df_statvideo_overview = read_csv_s3(bucket, file_statvideo_name)
df_weekvideo_overview = read_csv_s3(bucket, file_weekvideo_name)
df_video_log = read_csv_s3(bucket, file_videolog_name)
df_video_log = convert_to_datetime(column_name="Timestamp", df=df_video_log, tz="Australia/Adelaide")


# ######## Service ########
# ######## Semester Video Overview ########
service = VideoService("df_video")

week_th=service.define_whichweek(sem_start, sem_end, week_start, week_end)
print(f"This week is Week {week_th}th in the period of  {week_start} and {week_end} in the semester")

df_statvideo_overview = service.need_statvideo_columns(df_statvideo_overview)
df_weekvideo_overview = service.need_weekvideo_columns(df_weekvideo_overview)
df_weekvideo_overview = service.fix_week_overview(df_weekvideo_overview)
df_weekvideo_duration = service.map_weekvideo_videoduration(df_statvideo_overview, df_weekvideo_overview)
print(f"There are {len(df_weekvideo_overview)} unique videos in this course over the whole semester duirng {sem_start} to {sem_end}")
print(df_weekvideo_duration )

df_goupby_overview = service.groupby_week_overview(df_weekvideo_duration)
print("There are overview of every week video in this semester")
print(df_goupby_overview)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


# ######## Student Video Log ########
print("There are student video log")
print(df_video_log)
df_video_log = service.need_log_columns(df_video_log)
df_video_log = service.convert_to_mins(df_video_log)
print("~~~~~~~~ After need columns & convert to mins ~~~~~~~~~")
print(f"There are student video log during {week_start} and {week_end}")
print(df_video_log)
print(len(df_video_log))
print(df_video_log.columns)
print(df_video_log['Timestamp'].min())
print(df_video_log['Timestamp'].max())

df_summary=service.compute_per_video_stats(df_video_log)
print(f"Single Uerid video watching overview during {week_start} and {week_end}:")
print(df_summary)
print( df_summary.columns)

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


per_user, per_user_video, per_user_session_summary= service.summary_per_user_videolog(df_summary)
print(f"checking what is the per_user data look like after summary during {week_start} and {week_end}: ")
print(per_user)

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

print(f"checking what is the per_user_video data look like after summary during {week_start} and {week_end}:: ")
print(per_user_video)
print(per_user_video.columns)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

print(f"checking what is the per_user_session_video data look like after summary during {week_start} and {week_end}:: ")
print(per_user_session_summary)
print(per_user_session_summary.columns)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")



######################### Week_th_video_summary and sent the message content ################################################
##################################################################################################################################################
##################################################################################################################################################

print(f"checking this week {week_th}th during {week_start} and {week_end}:")
week_video_summary= df_goupby_overview[df_goupby_overview['Week'] == week_th]
print(week_video_summary)

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# remind_week_video_message=service.remind_week_videowatch(week_video_remind_messgae)
reminder_video_message=service.remind_week_videowatch(week_video_summary)
reminder_video_message

######################### Week_th_video_summary and sent the message content ################################################
##################################################################################################################################################
##################################################################################################################################################

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# print(week_video_summary)
print(df_weekvideo_duration)
print(df_weekvideo_duration.columns)
print(per_user_video)
print(per_user_video.columns)


######################### video weight importance ################################################
df_with_importance = service.video_weight_importance(df_weekvideo_duration)
print(df_with_importance)
df_user_video= service.map_weekvideo_duration_log(df_with_importance, per_user_video)

print(df_user_video)
print(df_user_video.columns)

######################### student watch competion percentage ################################################
userid_video_percent = service.percentage_video_watch(df_user_video)
print(userid_video_percent)

######################### the video engagement indicator ################################################
df_with_engagement = service.calculate_video_week_engagement(userid_video_percent)
print(df_with_engagement)


############# EDIT NEW ELEMENT INTO DURATION VIDEO FILE #################################################################
########### the version is when testing there is messing value on video duration #################################################################
###########  then we need to manually edit the video duration for the video #################################################################

print("NEED!!!!! Need to double check the Video with their missing video_duration")
nan_sessions = service.search_nan_session(df_with_engagement)
print(nan_sessions)

# Add a new video row
df_weekvideo_duration = service.edit_content_manually(df_weekvideo_duration,
                                  video_name='CURR 3021 W4 Evaluating Information BEYOND the CRAAP Test',
                                  week='W4',
                                  video_duration=5.14)

df_weekvideo_duration = service.edit_content_manually(df_weekvideo_duration,
                                  video_name='CURR 3021 - 1 ePortfolio',
                                  week=1,
                                  video_duration=5.3)

print("######################## AFTER manually edit the video name, week and duration ##########################################")
print(df_weekvideo_duration)
print(len(df_weekvideo_duration))


######################### do it again after edit video weight importance ################################################
print("######################## do it again after edit video weight importance  ##########################################")
df_with_importance = service.video_weight_importance(df_weekvideo_duration)
df_user_video= service.map_weekvideo_duration_log(df_with_importance, per_user_video)


userid_video_percent = service.percentage_video_watch(df_user_video)
print(userid_video_percent)
unique_userid=userid_video_percent['User ID'].nunique()
with pd.option_context('display.max_columns', None,  # show all columns
                       'display.max_rows', None,     # show all rows
                       'display.max_colwidth', None, # show full column content
                       'display.width', 200):        # widen display
        # Print column names
    print(userid_video_percent[userid_video_percent['User ID']== '05849c70-f2df-4c9c-a39b-b18f0024c997'])


# print("######################## do it again after edit video, output the engagement indicator ##########################################")
df_with_engagement = service.calculate_user_engagement_indicator(userid_video_percent)
print(f"the unique {unique_userid} User ID Video Engagement indicators during the {week_start} and {week_end}")
print(df_with_engagement)



threshold=0.3
reminder_df, triggered_ids = service.trigger_userid_sent_reminder(df_week_summary= week_video_summary, df_with_engagement= df_with_engagement , threshold=threshold)
print(reminder_df)
print(f"!!!!!!Reminder based on Video Eegagement Score and will reminder lower than threshold {threshold}")
with pd.option_context('display.max_columns', None,  # show all columns
                       'display.max_rows', None,     # show all rows
                       'display.max_colwidth', None, # show full column content
                       'display.width', 200):        # widen display
        # Print column names
    print(reminder_df[reminder_df['User ID']=='123f8000-cffb-4016-9f0c-a8eb001022ca'])
print(f"There are {len(triggered_ids)} ppl need to be remineded")
print(triggered_ids)

# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# print("one stduent")
# print(df_with_engagement[df_with_engagement['User ID']== '05849c70-f2df-4c9c-a39b-b18f0024c997'])


# print("second stduent")
# print(df_with_engagement[df_with_engagement['User ID']== 'e1e08bf2-9566-4bf9-bcb5-b11c00112442'])


# print(df_with_engagement[df_with_engagement['User ID']== 'f7843cbe-4560-4829-8d74-acb1000f6734'])

# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")



##### useful for analyzing the vidoe weekly data but now we look at the only current weekly data #####
# print("~~~~~~~~ After week sechedule ~~~~~~~~~")
# df_video_log= service.week_schedule(df_video_log, start = start)
# print(df_video_log)
# print(df_video_log.columns)


# print("~~~~~~~~ After groupby userid ~~~~~~~~~")
# userid_video= service.groupby_userid_week_watchvideo(df_video_log)
# print(userid_video)
# print(  userid_video.columns)


# userid_summary_video= service.summary_week_user_sessions(df_video_log)
# print(userid_summary_video)
# print(userid_summary_video.columns)




# ######## Build HTML Sections ########
# html_sections = []

# # Video Overview
# add_section(html_sections, f"Video Overview during {start} to {end}", df_video_overview.to_html(index=False, border=1), include_dates=True, start=start, end=end)
# add_section(html_sections, f"Video Weekly Overview during {start} to {end}", df_goupby_overview.to_html(index=False, border=1), include_dates=True, start=start, end=end)
