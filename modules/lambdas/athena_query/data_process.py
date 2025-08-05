import os
import sys

sys.path.append(os.path.split(os.path.abspath(__file__))[0])
from assign_duedate_query import *
from student_submission_time_query import *
from assign_cmid_section import *




def convert_time(df, time_col="time"):

    df = df.copy()

    # Convert UNIX timestamp to datetime
    dt_series = pd.to_datetime(df[time_col], unit='s')

    # Add readable full datetime
    df['Readable_Time'] = dt_series

    # Add time components
    df['Year'] = dt_series.dt.year
    df['Month'] = dt_series.dt.month
    df['Day'] = dt_series.dt.day
    df['Hour'] = dt_series.dt.hour
    df['Minute'] = dt_series.dt.minute
    df['Second'] = dt_series.dt.second

    return df


def rename_map_duedate(student_sub_df, assign_duedate_df):
    # Step 1: Rename columns with suffixes
    student_sub_df = student_sub_df.add_suffix('_student_sub')
    assign_duedate_df = assign_duedate_df.add_suffix('_assign_due')

    # Step 2: Merge on cmid
    merged_df = pd.merge(
        student_sub_df,
        assign_duedate_df,
        left_on='cmid_student_sub',
        right_on='cmid_assign_due',
        how='left'
    )
    return merged_df

def calculate_time_and_score(df, T_max=14, T_late=-2):
    df = df.copy()

    # Convert to datetime
    df['Readable_Time_student_sub'] = pd.to_datetime(df['Readable_Time_student_sub'])
    df['Readable_Time_assign_due'] = pd.to_datetime(df['Readable_Time_assign_due'])

    # Compute time differences
    time_diff = df['Readable_Time_assign_due'] - df['Readable_Time_student_sub']

    df['time_before_deadline_days'] = time_diff.dt.total_seconds() / 86400
    df['time_before_deadline_hours'] = time_diff.dt.total_seconds() / 3600

    # Normalize score based on days
    def normalize(t):
        if t >= T_max:
            return 1.0
        elif t >= 0:
            return t / T_max
        else:
            return max(0.0, 1 + t / abs(T_late))

    df['submission_score'] = df['time_before_deadline_days'].apply(normalize)

    return df


def full_assignment_submission_pipeline(course_id=4177):
    # Step 1: Load student submission data and convert time
    student_sub_df = student_data_transformation()
    student_sub_df = convert_time(student_sub_df, time_col="time")

    # Step 2: Load assignment cmid section and filter by course
    assign_cmid_section_df = cmid_section_df()
    filter_assign_cmid_section_df = filter_term_cmid(assign_cmid_section_df, course=course_id)
    filter_assign_cmid_section_df = convert_time(filter_assign_cmid_section_df, time_col="duedate")

    # Step 3: Merge the assignment due date info into the student submission data
    combined_df = rename_map_duedate(student_sub_df, filter_assign_cmid_section_df)

    # Step 4: Select only needed columns
    need_col = [
        'action_student_sub', 'cmid_student_sub', 'course_student_sub',
        'userid_student_sub', 'Readable_Time_student_sub',
        'assign_id_assign_due', 'assign_name_assign_due',
        'Readable_Time_assign_due'
    ]
    df = combined_df[need_col]

    # Step 5: Calculate time difference and score
    results = calculate_time_and_score(df)

    return results

# pipeline=full_assignment_submission_pipeline(course_id=4177)
# print(pipeline)
