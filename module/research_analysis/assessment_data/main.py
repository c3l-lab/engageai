
import os
import sys
import pandas as pd

# Get the current directory (assessment_data)
current_dir = os.path.dirname(__file__)

# Add the parent directory of current_dir (research_analysis) to sys.path
parent_dir = os.path.abspath(os.path.join(current_dir))
pa_parent_dir= os.path.abspath(parent_dir)
sys.path.append(os.path.split(parent_dir)[0])
sys.path.append(os.path.split(pa_parent_dir)[0])

# Now import custom modules
from assessment_data.read_csv_download import *
from assessment_data.function import *
from write_html import *

def main(grade_file: str, log_file: str, term_code: int, course_id: int, course: int):
    # Load CSV data
    csv_path = os.path.abspath(os.path.join(current_dir, '..', 'download_data'))
    grade_df = read_csv_from_module(csv_path, grade_file)
    log_df = read_csv_from_module(csv_path, log_file)

    # Filter final grade data for term and course
    term_grade_df = filter_by_column_value(grade_df, col_name='term_code', value=term_code)
    term_finalgrade_df = filter_by_column_value(term_grade_df, col_name='course_id', value=course_id)

    # Extract user info
    term_userid, term_username, term_user_count = extract_user_info(
        term_finalgrade_df, 'userid', 'username', term_code=term_code
    )

    distribution_df, distribution_fig = grade_distribution_with_plot(term_grade_df, term_code=term_code)

    # Grade Group Summary
    grade_group_df = assign_grade_group(term_grade_df)

    # Filter logs for course
    log_df = filter_by_column_value(log_df, col_name='course', value=course)

    # Match log with grade
    shared_ids_df, matched_log_df = check_uniqueid_in_finalgrade_log(
        log_df=log_df, grade_group_df=grade_group_df, term_code=term_code, course=course)

    # Process log time
    time_log_df = process_timestamp_and_split_hours(matched_log_df)

    # Weekly Summary
    weekly_summary = weekly_user_course_timebucket_summary(time_log_df)

    # Nudge Logic
    nudge_result = check_engagement_decline(weekly_summary, threshold=30)
    nudge_summary = summary_nudge_week(nudge_result)


    # Plotting
    summary_all_log_timebucket_plot_df, summary_all_log_timebucket_plot_fig= summary_log_timebucket_plot(time_log_df, course=course)
    summary_df, summary_fig  = plot_timebucket_by_week(weekly_summary)

    # Grades Group Analysis
    gradegroup_time_log_df = map_grade_group_to_time_log(time_log_df, grade_group_df)
    pivot_summary_df, pivot_summary_fig = plot_timebucket_x_stacked_grade(gradegroup_time_log_df)
    result_df, result_fig = plot_normalized_timebucket_x_stacked_grade(pivot_summary_df, grade_group_df)
    summary_time_log_df, summary_time_log_fig= plot_weekly_timebucket_stacked_by_grade(gradegroup_time_log_df)
    
    daily_grade_df, daily_grade_fig = generate_daily_timebucket_by_grade(gradegroup_time_log_df)
    # daily_summary_df, fig
    daily_summary_log_timebucket_plot_df, daily_summary_log_timebucket_plot_fig, daily_summary_log_timebucket_total_actions = daily_summary_log_timebucket_plot(daily_grade_df)

    # Additional weekday-wise plot
    melted, melted_fig= plot_weekday_timebucket_grade_distribution(daily_grade_df)
    
    normalized_df = normalize_action_with_group_info(melted,grade_group_df)
    # normalized_df_peruser, normalized_df_peruser_fig = plot_weekday_timebucket_grade_distribution_per_user(normalized_df)
    normalized_df_peruser, normalized_df_peruser_week_figs  = plot_weekday_timebucket_grade_distribution_per_user(normalized_df)

    # ---- Collect and export results ----
    df_dict = {
        "term_finalgrade_df": term_finalgrade_df,
        "term_user_count": term_user_count,
        "term_unique_userid": term_userid, 
        "term_unique_username": term_username, 
        "distribution_df": distribution_df,
        "grade_group_df": grade_group_df,
        "shared_ids_df": shared_ids_df,
        "matched_log_df": matched_log_df,
        "time_log_df": time_log_df,
        "weekly_user_course_timebucket_summary": weekly_summary,
        "nudge_result": nudge_result,
        "nudge_summary": nudge_summary,
        "summary_all_log_timebucket_plot_df": summary_all_log_timebucket_plot_df, 
        "plot_timebucket_by_week":  summary_df,
        " gradegroup_time_log_df": gradegroup_time_log_df,
        " plot_timebucket_x_stacked_grade":pivot_summary_df,
        "plot_normalized_timebucket_x_stacked_grade": result_df,
        "plot_weekly_timebucket_stacked_by_grade": summary_time_log_df,
        "generate_daily_timebucket_by_grade":  daily_grade_df,
        "daily_summary_log_timebucket_plot_df": daily_summary_log_timebucket_plot_df,
        "daily_summary_log_timebucket_total_actions": daily_summary_log_timebucket_total_actions,
        "plot_weekday_timebucket_grade_distribution": melted,
        "normalize_action_with_group_info":normalized_df,
        "plot_weekday_timebucket_grade_distribution_per_user": normalized_df_peruser
    
    }


    plot_dict = {'Grade Distribution Plot': distribution_fig,
                 'Summary all Log Timebucket Plot':summary_all_log_timebucket_plot_fig,
                #   "summary_df Plot": summary_fig ,
                  "plot_timebucket_by_week": summary_fig,
                  'plot_timebucket_x_stacked_grade':pivot_summary_fig,
                  'plot_normalized_timebucket_x_stacked_grade':result_fig, 
                  'plot_weekly_timebucket_stacked_by_grade': summary_time_log_fig,
                  'generate_daily_timebucket_by_grade':daily_grade_fig
                #   "daily_summary_log_timebucket_plot":  **extract_figures(daily_summary_log_timebucket_plot_fig),
                #   'plot_weekday_timebucket_grade_distribution':**extract_figures(melted_fig),
                #     'plot_weekday_timebucket_grade_distribution_per_user': **extract_figures(normalized_df_peruser_week_figs),

                 }

    # Merge additional multi-figure plots
    plot_dict.update(extract_figures(daily_summary_log_timebucket_plot_fig))
    plot_dict.update(extract_figures(melted_fig))
    plot_dict.update(extract_figures(normalized_df_peruser_week_figs))



    output_dir = os.path.join(current_dir, "visualisation_data")
    save_dataframe_and_plots_to_html(df_dict, plot_dict,term_code=term_code, kind_analysis=kind_analysis)



if __name__ == '__main__':
    # You can customize these values or pass via argparse later
    grade_file = 'allterm_course163601_finalgrade.csv'
    log_file = 'term2405_course3547_alllog.csv'
    term_code = 2405
    course_id = 163601
    course = 3547
    kind_analysis="gradegroup_assessment_summary"

    main(grade_file, log_file, term_code, course_id, course)



# import os
# import sys
# import pandas as pd


# # Get the current directory (assessment_data)
# current_dir = os.path.dirname(__file__)

# # Add the parent directory of current_dir (research_analysis) to sys.path
# parent_dir = os.path.abspath(os.path.join(current_dir))
# # head = os.path.split(parent_dir)[0]
# sys.path.append(os.path.split(parent_dir)[0])

# # Now you can import your modules
# from assessment_data.read_csv_download import *
# from assessment_data.function import *

# # ---- Load CSV Data ----
# csv_path = os.path.join(current_dir, '..', 'download_data')
# csv_path = os.path.abspath(csv_path)  # make it absolute path

# grade_df = read_csv_from_module(csv_path,'allterm_course163601_finalgrade.csv')
# log_df = read_csv_from_module(csv_path,'term2405_course3547_alllog.csv')

# # ---- Filter final grade data for term 2405 ----
# term_code = 2405
# course_id = 163601
# course=3547

# term_grade_df = filter_by_column_value(grade_df, col_name='term_code', value= term_code)
# term_finalgrade_df = filter_by_column_value(term_grade_df, col_name='course_id', value=course_id )

# term_userid, term_username, term_user_count = extract_user_info(
#     term_finalgrade_df, 'userid', 'username', term_code= term_code
# )
# # ---- Grade Distribution ----
# distribution_df = grade_distribution_with_plot(term_grade_df, term_code=term_code)
# print(distribution_df)

# # ---- Grade Group Summary ----
# grade_group_df = assign_grade_group(term_grade_df)

# # ---- Filter logs for course ----
# log_df = filter_by_column_value(log_df, col_name='course', value=course )

# # ---- Match log with grade ----
# shared_ids_df, matched_log_df = check_uniqueid_in_finalgrade_log(
#     log_df=log_df, grade_group_df=grade_group_df, term_code=term_code, course=course)

# # Optional: explore the results
# print(shared_ids_df)
# print(matched_log_df)

# # ---- Process log time ----
# time_log_df = process_timestamp_and_split_hours(matched_log_df)
# print(time_log_df)

# # ---- Weekly Summary ----
# weekly_summary = weekly_user_course_timebucket_summary(time_log_df)
# print(weekly_summary)

# # ---- Nudge Logic ----
# nudge_result = check_engagement_decline(weekly_summary, threshold=30)
# nudge_summary = summary_nudge_week(nudge_result)
# print(nudge_result)
# print(nudge_summary)

# # ---- Plotting ----
# summary_all_log_timebucket_plot=summary_log_timebucket_plot(time_log_df, course=course)
# print(summary_all_log_timebucket_plot)
# summary_df=plot_timebucket_by_week(weekly_summary)
# print(summary_df)

# # ---- Grades Group ----

# gradegroup_time_log_df = map_grade_group_to_time_log(time_log_df, grade_group_df)
# gradegroup_time_log_df

# pivot_summary_df = plot_timebucket_x_stacked_grade(gradegroup_time_log_df)
# pivot_summary_df

# result_df = plot_normalized_timebucket_x_stacked_grade(pivot_summary_df, grade_group_df)
# result_df

# summary_df = plot_weekly_timebucket_stacked_by_grade(gradegroup_time_log_df)
# summary_df

# daily_grade_df = generate_daily_timebucket_by_grade(gradegroup_time_log_df)
# daily_grade_df

# daily_summary_log_timebucket_plot_df=daily_summary_log_timebucket_plot(daily_grade_df)
# print(daily_summary_log_timebucket_plot_df)

# # Example usage:
# melted = plot_weekday_timebucket_grade_distribution(daily_grade_df)
# melted

# normalized_df = normalize_action_with_group_info(melted, term_grade_df)
# normalized_df

# normalized_df_peruser=plot_weekday_timebucket_grade_distribution_per_user(normalized_df)
# normalized_df_peruser