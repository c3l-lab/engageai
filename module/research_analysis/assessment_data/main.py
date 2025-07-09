import os
import sys
import pandas as pd


# Get the current directory (assessment_data)
current_dir = os.path.dirname(__file__)

# Add the parent directory of current_dir (research_analysis) to sys.path
parent_dir = os.path.abspath(os.path.join(current_dir))
# head = os.path.split(parent_dir)[0]
sys.path.append(os.path.split(parent_dir)[0])

# Now you can import your modules
from assessment_data.read_csv_download import *
from assessment_data.function import *

# ---- Load CSV Data ----
csv_path = os.path.join(current_dir, '..', 'download_data')
csv_path = os.path.abspath(csv_path)  # make it absolute path

grade_df = read_csv_from_module(csv_path,'allterm_course163601_finalgrade.csv')
log_df = read_csv_from_module(csv_path,'term2405_course3547_alllog.csv')

# ---- Filter final grade data for term 2405 ----
term_code = 2405
course_id = 163601
course=3547

term_grade_df = filter_by_column_value(grade_df, col_name='term_code', value= term_code)
term_finalgrade_df = filter_by_column_value(term_grade_df, col_name='course_id', value=course_id )

term_userid, term_username, term_user_count = extract_user_info(
    term_finalgrade_df, 'userid', 'username', term_code= term_code
)
print(len(term_finalgrade_df))

# ---- Grade Distribution ----
distribution_df = grade_distribution_with_plot(term_grade_df, term_code=term_code)
print(distribution_df)

# ---- Grade Group Summary ----
grade_group_df = assign_grade_group(term_grade_df)

# ---- Filter logs for course ----
log_df = filter_by_column_value(log_df, col_name='course', value=course )

# ---- Match log with grade ----
shared_ids_df, matched_log_df = check_uniqueid_in_finalgrade_log(
    log_df=log_df, grade_group_df=grade_group_df, term_code=term_code, course=course)

# Optional: explore the results
print(shared_ids_df)
print(matched_log_df)

# ---- Process log time ----
time_log_df = process_timestamp_and_split_hours(matched_log_df)
print(time_log_df)

# ---- Weekly Summary ----
weekly_summary = weekly_user_course_timebucket_summary(time_log_df)
print(weekly_summary)

# ---- Nudge Logic ----
nudge_result = check_engagement_decline(weekly_summary, threshold=30)
nudge_summary = summary_nudge_week(nudge_result)
print(nudge_result)
print(nudge_summary)

# ---- Plotting ----
summary_all_log_timebucket_plot=summary_log_timebucket_plot(time_log_df, course=course)
print(summary_all_log_timebucket_plot)
summary_df=plot_timebucket_by_week(weekly_summary)
print(summary_df)