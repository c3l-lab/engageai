import os
import sys
import pandas as pd
from pydantic import BaseModel
from typing import Optional
# Get the current directory (assessment_data)
current_dir = os.path.abspath(os.path.dirname(__file__))

# Add the parent directory of current_dir (research_analysis) to sys.path
sys.path.append(os.path.sep.join(current_dir.split(os.path.sep)[:-1]))
sys.path.append(os.path.sep.join(current_dir.split(os.path.sep)[:-2]))

# parent_dir = os.path.abspath(os.path.split(current_dir)[0])
# pa_parent_dir= os.path.abspath(parent_dir)
# pa_pa_parent_dir=os.path.abspath(os.path.split(pa_parent_dir)[0])

# sys.path.append(os.path.split(parent_dir)[0])
# sys.path.append(os.path.split(pa_parent_dir)[0])
# sys.path.append(os.path.split(pa_pa_parent_dir)[0])


# Now import custom modules
from data_pipeline.data_aws_import_singledf import *
from read_csv_download import *
# from read_singlecsv_from_s3 import *
from submission_data.function import *
from assessment_data.function import *
from write_html import *
from convert_time import *



class CourseItem(BaseModel):
    term_code: int
    '''study period code'''
    course_id: int
    '''course online id'''
    course: int    
    '''moodle course id'''

class Assignment(BaseModel):
    name: str
    cmid: int

class PlotOption(BaseModel):
    T_max: int
    T_late: int
    bin_hours: int=24
    kind_analysis: str

class BucketConfig(BaseModel):
    name: str
    grade_file: str
    log_file: str
    assign_due_file: str
    region: Optional[str] = 'ap-southeast-2'


# def main(bucket_name: str, grade_file: str, log_file: str, assign_due_file: str, term_code: int, course_id: int, course: int,
#         useerid: int, assign_name: str, assign_cmid: int, T_max: int, T_late: int, bin_hours, kind_analysis: str):
def main(
        bucket_config: BucketConfig, 
        userid: str, 
        course_obj: CourseItem, 
        assign_obj:Assignment,
        options:PlotOption
    ):
    bucket_name = bucket_config.name
    grade_file = bucket_config.grade_file
    log_file = bucket_config.log_file
    assign_due_file = bucket_config.assign_due_file
    term_code = course_obj.term_code
    course_id = course_obj.course_id
    course = course_obj.course
    assign_name= assign_obj.name
    assign_cmid= assign_obj.cmid
    T_max=options.T_max
    T_late=options.T_late
    bin_hours=options.bin_hours
    kind_analysis=options.kind_analysis

    # # Load CSV data
    # csv_path = os.path.abspath(os.path.join(current_dir, '..', 'download_data'))
    # grade_df = read_csv_from_module(csv_path, grade_file)
    # log_df = read_csv_from_module(csv_path, log_file)
    # assigndue_file= read_csv_from_module(csv_path, assign_due_file)

    log_df= read_single_csv_from_s3(log_file, bucket_name)
    grade_df = read_single_csv_from_s3(grade_file, bucket_name)

    # Filter final grade data for term and course
    term_grade_df = filter_by_column_value(grade_df, col_name='term_code', value=term_code)
    term_finalgrade_df = filter_by_column_value(term_grade_df, col_name='course_id', value=course_id)

    # Extract user info
    term_userid, term_username, term_user_count = extract_user_info(
        term_finalgrade_df, 'userid', 'username', term_code=term_code
    )

    submit_df = filter_col_value_userid(
        df=log_df,
        col='action',
        value='submit for grading',
        user_id=term_userid
    )
    time_submit_df = convert_time(submit_df,time_col='time')
    # latest_submission_df = fetch_latest_submittime(time_submit_df, userid)
    latest_submission_df = fetch_latest_submittime(time_submit_df)

######### TEMP DUEDATE ASSIGN DATE FOR TOMMYCODE
    parsed_dates = df.apply(parse_date, axis=1, result_type='expand')
    result_df = pd.concat([df, parsed_dates], axis=1)

    # parsed_dates = grade_df.apply(parse_date, axis=1, result_type='expand')
    # result_df = pd.concat([grade_df, parsed_dates], axis=1)

###########

    combined = merge_assign_and_submissions(
        assign_duedate=result_df,
        student_submittime=latest_submission_df ,
        assign_name=assign_name,
        assign_cmid=assign_cmid
    )

    print(combined)

    summary = summarize_submissions_by_6hour_bins(combined)
    summary

    plot_assign_and_submissions_df,plot_assign_and_submissions_fig=plot_assign_and_submissions(combined)
    plot_submission_density_around_due_df,plot_submission_density_around_due_fig=plot_submission_density_around_due(combined)

    # # Grade Group Summary
    grade_group_df = assign_grade_group(term_grade_df)
    sub_grade_df= map_grade_group(combined,grade_group_df)
    sub_grade_df

    # df_result = calculate_time_and_score(sub_grade_df)
    # df_result
    df_result = calculate_time_and_score(sub_grade_df, T_max=7, T_late=-2)
    df_result

        # overall_summary, user_summary, grade_summary = summarize_submission_scores(df_result)
    overall_summary, grade_summary = summarize_submission_scores(df_result)

    # Optional: display or save
    print("🔹 Overall Submission Summary:\n", overall_summary)
    # print("\n🔹 Per-User Submission Summary:\n", user_summary.head())
    print("\n🔹 Per-Grade Submission Summary:\n", grade_summary)

    # # For 6-hour bins
    # summary_6hr = summarize_submissions_by_bins_grade_group(sub_grade_df, bin_hours)
    # summary_6hr

    summary_1day = summarize_submissions_by_bins_grade_group(sub_grade_df, bin_hours)
    summary_1day

        # Example usage
    early_late_summary_grade_group = summarize_early_late_counts(summary_1day)
    early_late_summary_grade_group

    plot_assign_and_submissions_by_grade_df,plot_assign_and_submissions_by_grade_fig=plot_assign_and_submissions_by_grade(sub_grade_df)
    plot_submission_density_by_grade_df, plot_submission_density_by_grade_fig=plot_submission_density_by_grade(sub_grade_df)
    plot_assign_and_submissions_by_grade_per_user_df,plot_assign_and_submissions_by_grade_per_user_fig=plot_assign_and_submissions_by_grade_per_user(sub_grade_df)
    plot_submission_density_by_grade_per_user_df, plot_submission_density_by_grade_per_user_fig=plot_submission_density_by_grade_per_user(sub_grade_df)

    # Prepare results for saving
    df_dict = {
        "term_userid": term_userid,
        "term_username": term_username,
        "term_user_count":term_user_count,
        "Combined Submission": combined,
        "Summary (6-hour bins)": summary,
        "plot_assign_and_submissions_df":plot_assign_and_submissions_df,
        "plot_submission_density_around_due_df":plot_submission_density_around_due_df,
        "Submission+Grade Group": sub_grade_df,
        "Submission Score Result": df_result,
        "Overall Summary": overall_summary,
        "Grade Summary": grade_summary,
        "Summary by Day": summary_1day,
        "Early/Late Summary by Grade Group": early_late_summary_grade_group,
        "plot_assign_and_submissions_by_grade_df":plot_assign_and_submissions_by_grade_df,
        "plot_submission_density_by_grade_df":plot_submission_density_by_grade_df,
        "plot_assign_and_submissions_by_grade_per_user_df":plot_assign_and_submissions_by_grade_per_user_df,
        "plot_submission_density_by_grade_per_user_df":plot_submission_density_by_grade_per_user_df,
        "Grade Group Table": grade_group_df
    }

    plot_dict = {
        "Assignment vs Submissions": plot_assign_and_submissions_fig,
        "Submission Density Around Due": plot_submission_density_around_due_fig,
        "Submission by Grade": plot_assign_and_submissions_by_grade_fig,
        "Density by Grade": plot_submission_density_by_grade_fig,
        "Submissions by Grade per User": plot_assign_and_submissions_by_grade_per_user_fig,
        "Density by Grade per User": plot_submission_density_by_grade_per_user_fig
    }

    # Save to HTML
    # output_dir = os.path.join(current_dir, "submission_data")
    # os.makedirs(output_dir, exist_ok=True)
    # output_dir = os.path.join(current_dir, "submission_data")
    save_dataframe_and_plots_to_html(df_dict, plot_dict,term_code=term_code, kind_analysis=kind_analysis)


if __name__ == '__main__':
    bucket_name= "engage-ai-dataset"

    # grade_file = 'allterm_course163601_finalgrade.csv'
    # log_file = 'term2405_course3547_alllog.csv'
    # assign_due_file = 'every_termcode_assign_module_duedate.csv'

    course_obj = CourseItem(
        term_code=2405,
        course_id=163601,
        course = 3547
    )

    assign_obj = Assignment(
        name = 'Assessment: Research Plan',
        cmid = 687632
    )

    options = PlotOption(
        T_max = 7,
        T_late = -2,
        bin_hours = 24,
        kind_analysis = "gradegroup_submission_summary"
    )
    userid = 94005

    bucket_config = BucketConfig(
        name='engage-ai-dataset',
        grade_file = 'allterm_course163601_finalgrade.csv',
        log_file = 'term2405_course3547_alllog.csv',
        assign_due_file = 'every_termcode_assign_module_duedate.csv'

    )
    # term_code = 2405
    # course_id = 163601
    # course = 3547
    # assign_name = 'Assessment: Research Plan'
    # assign_cmid = 687632
    # T_max = 7
    # T_late = -2
    # bin_hours = 24
    # kind_analysis = "gradegroup_submission_summary"

    # main(bucket_name, grade_file, log_file, assign_due_file, term_code, course_id, course, userid,
    #      assign_name, assign_cmid, T_max, T_late, bin_hours, kind_analysis)
    main(bucket_config, userid, course_obj, assign_obj, options)


# # naming conventions
# * snake case: paremeter
# * camel case: Class
# * CONST 
