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

    firstview_df = filter_col_value_userid(
        df=log_df,
        col='module',
        value='assign',
        user_id=term_userid
    )

    time_firstview_df = convert_time(firstview_df,time_col='time')
    all_first_views = groupby_userid_firstview(time_firstview_df)

    grade_group_df = assign_grade_group(term_grade_df)
    sub_grade_df= map_grade_group(all_first_views,grade_group_df)

    assign_mapping_df = pd.DataFrame(data)


    ######### TEMP DUEDATE ASSIGN DATE FOR TOMMYCODE
    parsed_dates = df.apply(parse_date, axis=1, result_type='expand')
    result_df = pd.concat([df, parsed_dates], axis=1)
    ###########

    merged = merge_assignments_all_sources(
        assign_duedate=result_df,
        student_firstview_df=sub_grade_df,
        assign_mapping_df= assign_mapping_df
        # assign_name='Assessment: Research Plan',
        # assign_cmid=687632
    )

    scored_df, summary = process_first_view_scores(merged, cmid_value=None,T_max= T_max, T_late= T_late)
    scored_df

    # Result dictionary
    df_dict = {
        "First View Scores": scored_df,
        "Summary": summary,
        "Grade Group Mapping": grade_group_df,
        "First Views": all_first_views
    }

    # Save to HTML
    output_dir = os.path.join(current_dir, "firstview_data")
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
    kind_analysis="gradegroup_firstview_summary"

    main(grade_file, log_file, assign_due_file, term_code, course_id, course, 
         assign_name, assign_cmid,T_max, T_late)




