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
from read_csv_download import *
from submission_data.function import *
from assessment_data.function import *
from firstview_data.function import *
from assign_pre_48hrs.function import *
from write_html import *
from convert_time import *

def main(grade_file: str, log_file: str, assign_due_file: str, term_code: int, course_id: int, course: int,
        assign_name: str, assign_cmid: int, T_max: int, T_late: int, ):

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

    converted_time_df=convert_time(log_df)
    grade_group_df = assign_grade_group(term_grade_df)
    page_48hour= map_grade_group(converted_time_df,grade_group_df)
    page_48hour

    ########## TEMP DUEDATE ASSIGN DATE FOR TOMMYCODE
    parsed_dates = df.apply(parse_date, axis=1, result_type='expand')
    result_df = pd.concat([df, parsed_dates], axis=1)
    # ###########

    merged = merge_assignments_all_sources(
        assign_duedate=result_df,
        student_firstview_df=page_48hour,
        assign_mapping_df= assign_mapping_df,
        assign_name= assign_name,
        assign_cmid= assign_cmid
    )

    filtered_df = filter_col_value_userid(
    df=merged,
    col='module',
    value='assign',
    user_id=term_userid
    )

    new_filtered_df = filter_col_value_userid(
    df=filtered_df,
    col='action',
    value='view',
    user_id=term_userid
    )

    hour48_df=check_48hour_view_count(new_filtered_df, threshold_hour=48)
    summary_df = summarize_action_counts(hour48_df)

    df_dict = {
        "Final Grade Data": term_finalgrade_df,
        "Log with Time Converted": converted_time_df,
        "Grade Grouped Logs": page_48hour,
        "Assignment Mapping": assign_mapping_df,
        "Merged Assignments and Logs": merged,
        "Filtered Logs (assign module)": filtered_df,
        "Filtered Logs (view actions)": new_filtered_df,
        "48-hour View Count": hour48_df,
        "Action Count Summary": summary_df
    }

    # Save to HTML
    output_dir = os.path.join(current_dir, "assign_pre_48hrs_data")
    os.makedirs(output_dir, exist_ok=True)
    save_dataframe_and_plots_to_html(df_dict,term_code=term_code, kind_analysis=kind_analysis)


if __name__ == '__main__':
    # You can customize these values or pass via argparse later
    grade_file = 'allterm_course163601_finalgrade.csv'
    log_file = 'term2405_course3547_alllog.csv'
    assign_due_file= 'every_termcode_assign_module_duedate.csv'
    term_code = 2405
    course_id = 163601
    course = 3547
    # userid = 94005
    assign_name='Assessment: Research Plan'
    assign_cmid=687632
    T_max= 21
    T_late= -2
    # bin_hours=24
    kind_analysis="gradegroup_assign_pre_48hrs_data_summary"

    main(grade_file, log_file, assign_due_file, term_code, course_id, course, 
         assign_name, assign_cmid,T_max, T_late)




