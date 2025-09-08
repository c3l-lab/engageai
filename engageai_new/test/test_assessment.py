import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.readcsv_writehtml import read_csv_s3, write_html, add_section, save_html_s3
from src.service.assessment import AssessmentService

######## Config ########
bucket = "engage-ai-raw-dataset"
start = "14/07/2025"
end = "21/07/2025"
file_duedate_name = "engageai_weekly_assessment/term_assign_duedate.csv"
file_log_name = "engageai_weekly_assessment/testing_subtime_20250714_0721.csv"

######## Read CSV File ########
df_duedate = read_csv_s3(bucket, file_duedate_name)
df_log = read_csv_s3(bucket, file_log_name)

######## Service ########
service = AssessmentService(df_duedate, df_log)

df_duedate = service.convert_to_datetime("duedate", df=df_duedate, tz="Australia/Adelaide")
df_duedate = service.get_latest_due_date(df=df_duedate)
df_duedate = df_duedate.sort_values(['duedate', 'cmid']).reset_index(drop=True)

df_log = service.log_to_action_time(df_log)
week_log = service.filter_actions_by_period(df_log, col_name="time", start=start, end=end)
df_sub_log = service.get_action_submit(week_log, start=start, end=end)

######## Build HTML Sections ########
html_sections = []

# Duedates
add_section(html_sections, "Assessment Due Dates", df_duedate.to_html(index=False, border=1), include_dates=True, start=start, end=end)

# Weekly submissions
if df_sub_log.empty:
    add_section(html_sections, "Weekly Submissions", f"<p>No submissions required between {start} and {end}</p>", include_dates=True, start=start, end=end)
else:
    userid_submissions_dup, grouped = service.groupby_userid_submissiontime(df=df_sub_log)
    userid_submissions = service.get_latest_userid_subtime(userid_submissions_dup)

    merged = pd.merge(userid_submissions, df_duedate, on="cmid", how="left")
    summary = merged.groupby(["cmid", "assign_name", "duedate"])["userid"].nunique().reset_index()
    add_section(html_sections, "Weekly Submission Summary", summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)

    new_df = service.attach_due_date_from_df(df_duedate=df_duedate, userid_submissions=userid_submissions).calculate_time_score(T_max=14, T_late=-2).merged_df
    add_section(html_sections, "Submission Scores", new_df.to_html(index=False, border=1), include_dates=True, start=start, end=end)

    assign_summary, student_summary, semester_summary = service.summarize_scores()
    add_section(html_sections, "Per Assignment Submission Score", assign_summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)
    add_section(html_sections, "Per Student Submission Score", student_summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)
    add_section(html_sections, "Semester Overall Score", semester_summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)

    early_late_summary, per_student_summary, per_assignment_summary = service.summarize_early_late_counts(new_df)
    add_section(html_sections, "Early vs Late (All Assignments)", early_late_summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)
    add_section(html_sections, "Early vs Late (Per Student)", per_student_summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)
    add_section(html_sections, "Early vs Late (Per Assignment)", per_assignment_summary.to_html(index=False, border=1), include_dates=True, start=start, end=end)

    score_threshold = 0.2
    low_score_df, trigger_userids = service.generate_submission_index_trigger_users(score_threshold=score_threshold)
    add_section(html_sections, f"Users Below Threshold {score_threshold}", low_score_df.to_html(index=False, border=1), include_dates=True, start=start, end=end)
    add_section(html_sections, f"There are {len(trigger_userids)} User IDs to Remind", f"<p>{trigger_userids}</p>")

######## Generate HTML ########
html_content = write_html(html_sections, start=start, end=end)

######## Upload to S3 ########
save_html_s3(html_content, start=start, end=end)
