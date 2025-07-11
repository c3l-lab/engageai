def groupby_userid_firstview(df, userid=None, cmid_value=None):

    df = df.copy()

    # Optional filtering by userid
    if userid:
        df = df[df['userid'] == int(userid)]

    # Optional filtering by cmid
    if cmid_value:
        df = df[df['cmid'] == int(cmid_value)]

    # Group and get first view Readable_Time
    grouped = df.groupby(['userid', 'cmid'], as_index=False)['Readable_Time'].min()
    grouped = grouped.rename(columns={'Readable_Time': 'first_view_time'})

    return grouped


########## TOMMEY CODE FOR MAPPING ASSIGN WITH ASSIGN_NAME AND CMID
import pandas as pd

# Define the data as a list of dictionaries
data = [
    {
        "assign_NAME": "Assessment: Research Plan",
        "DUE_DATE": "12 pm Monday 22 January",
        "cmid": 687632,
        "term_code": 2405,
        "course": 3547
    },
    {
        "assign_NAME": "Assessment: Search and evaluate",
        "DUE_DATE": "12 pm Monday 5 February",
        "cmid": 687640,
        "term_code": 2405,
        "course": 3547
    },
    {
        "assign_NAME": "Assessment: Referencing quiz",
        "DUE_DATE": "12 pm Monday 12 February",
        "cmid": None,
        "term_code": 2405,
        "course": 3547
    },
    {
        "assign_NAME": "Assessment: Data quiz",
        "DUE_DATE": "12 pm Monday 19 February",
        "cmid": None,
        "term_code": 2405,
        "course": 3547
    },
    {
        "assign_NAME": "Assessment: Academic writing quiz",
        "DUE_DATE": "12 pm Monday 4 March",
        "cmid": None,
        "term_code": 2405,
        "course": 3547
    },
    {
        "assign_NAME": "Assessment: Reflective video",
        "DUE_DATE": "Friday 15 March 5 pm",
        "cmid": 687659,
        "term_code": 2405,
        "course": 3547
    },
    {
        "assign_NAME": "Assessment 2: Report (40%)",
        "DUE_DATE": "12 pm Monday 11 March",
        "cmid": 687665,
        "term_code": 2405,
        "course": 3547
    },
]

# Convert to DataFrame
assign_mapping_df = pd.DataFrame(data)


##################


def merge_assignments_all_sources(
    assign_duedate,
    assign_mapping_df,
    student_firstview_df,
    assign_name=None,
    assign_cmid=None
):


    # Optional filtering
    if assign_name is not None:
        assign_duedate = assign_duedate[assign_duedate['Name'] == assign_name]
        assign_mapping_df = assign_mapping_df[assign_mapping_df['assign_NAME'] == assign_name]

    if assign_cmid is not None:
        assign_mapping_df = assign_mapping_df[assign_mapping_df['cmid'] == assign_cmid]
        student_firstview_df = student_firstview_df[student_firstview_df['cmid'] == assign_cmid]

    # Step 1: Merge assign_duedate with assign_mapping_df using assignment name
    merged_duedate_mapping = pd.merge(
        assign_duedate,
        assign_mapping_df,
        left_on='Name',
        right_on='assign_NAME',
        how='left',
        suffixes=('', '_map')
    )

    # Step 2: Merge result with student_firstview_df on cmid
    final_merged = pd.merge(
        student_firstview_df,
        merged_duedate_mapping,
        on='cmid',
        how='left'
    )
    # final_merged=final_merged.dropna(subset=['cmid'], inplace=True)
    # df.dropna(subset=['cmid'], inplace=True)

    final_merged = final_merged[final_merged['cmid'] != 0]
    final_merged.dropna(subset=['cmid'], inplace=True)

    return final_merged

import pandas as pd

def calculate_time_and_score_modified(df, T_max:int, T_late:int):
    df = df.copy()
    
    # Convert to datetime
    df['first_view_time'] = pd.to_datetime(df['first_view_time'])
    df['Readable_Time_assign_date'] = pd.to_datetime(df['Readable_Time_assign_date'])

    # Compute time difference: assign date - first view
    time_diff = df['Readable_Time_assign_date'] - df['first_view_time']

    df['first_view_time_before_deadline_days'] = time_diff.dt.total_seconds() / 86400
    df['first_view_time_before_deadline_hours'] = time_diff.dt.total_seconds() / 3600

    # Normalization function
    def normalize(t):
        if t >= T_max:
            return 1.0
        elif t >= 0:
            return t / T_max
        else:
            return max(0.0, 1 + t / abs(T_late))

    df['first_time_view_score'] = df['first_view_time_before_deadline_days'].apply(normalize)

    return df


def process_first_view_scores(df, cmid_value=None, T_max=int, T_late=int):
    df = df.copy()

    # Rename Readable_Time to Readable_Time_assign_date
    if 'Readable_Time' in df.columns:
        df = df.rename(columns={'Readable_Time': 'Readable_Time_assign_date'})

    # Filter by cmid if provided and cmid column exists
    if cmid_value is not None and 'cmid' in df.columns:
        df = df[df['cmid'] == cmid_value]

    # Drop rows with missing critical columns to avoid errors
    df = df.dropna(subset=['first_view_time', 'Readable_Time_assign_date', 'grade_group_matched', 'cmid', 'userid'])

    # Group by cmid, grade_group_matched, userid; aggregate first_view_time as mean, assign date as first
    grouped = df.groupby(['cmid', 'grade_group_matched', 'userid'], as_index=False).agg({
        'first_view_time': 'first',
        'Readable_Time_assign_date': 'first',
        'Name':'first'
    })

    # Calculate scores per group
    scored_df = calculate_time_and_score_modified(grouped, T_max=T_max, T_late=T_late)

    # Custom sorting order for grade_group_matched
    custom_order = ['hd', 'cd', 'p', 'f', 'i']  # add more if needed

    # Create a categorical type for custom sorting
    scored_df['grade_group_matched'] = pd.Categorical(
        scored_df['grade_group_matched'],
        categories=custom_order,
        ordered=True
    )

    # Sort by cmid ascending, then by grade_group_matched by custom order
    scored_df = scored_df.sort_values(['cmid', 'grade_group_matched']).reset_index(drop=True)

    # Summary per cmid and grade_group_matched: average, median, min, max of first_time_view_score
    summary = scored_df.groupby(['cmid', 'grade_group_matched'], observed=False).agg(
        average_first_view_score=('first_time_view_score', 'mean'),
        median_first_view_score=('first_time_view_score', 'median'),
        min_first_view_score=('first_time_view_score', 'min'),
        max_first_view_score=('first_time_view_score', 'max'),
         Name=('Name', 'first')  # Keep first Name in each group
    ).reset_index()



    return scored_df, summary
