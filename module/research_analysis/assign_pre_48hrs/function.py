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

def check_48hour_view_count(df, threshold_hour=48, userid=None, cmid=None):
    required_cols = ['userid', 'cmid', 'action', 'Readable_Time_x', 'Readable_Time_y', 'grade_group_matched']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Optional filtering
    if userid is not None:
        df = df[df['userid'] == userid]
    if cmid is not None:
        df = df[df['cmid'] == cmid]

    # Copy and rename columns
    df_filtered = df.copy()
    df_filtered = df_filtered.rename(columns={
        'Readable_Time_x': 'Readable_Time_action',
        'Readable_Time_y': 'Readable_Time_duedate'
    })

    # Convert time columns
    df_filtered['Readable_Time_action'] = pd.to_datetime(df_filtered['Readable_Time_action'])
    df_filtered['Readable_Time_duedate'] = pd.to_datetime(df_filtered['Readable_Time_duedate'])

    # Calculate the lower bound time
    df_filtered['Readable_Time_Before_Xhrs'] = df_filtered['Readable_Time_duedate'] - pd.to_timedelta(threshold_hour, unit='h')

    # Filter for actions within the window
    df_within_window = df_filtered[
        (df_filtered['Readable_Time_action'] >= df_filtered['Readable_Time_Before_Xhrs']) &
        (df_filtered['Readable_Time_action'] <= df_filtered['Readable_Time_duedate'])
    ]

    # Group and aggregate
    grouped = df_within_window.groupby(['userid', 'cmid']).agg(
        Readable_24hrs_before_action_counts=('action', 'size'),
        Readable_Time_duedate=('Readable_Time_duedate', 'first'),
        Readable_Time_Before_Xhrs=('Readable_Time_Before_Xhrs', 'first'),
        grade_group_matched=('grade_group_matched', 'first')
    ).reset_index()

    return grouped


def summarize_action_counts(hour48_df):
    # Step 1: Group by cmid and grade_group_matched to compute summary statistics
    summary = hour48_df.groupby(['cmid', 'grade_group_matched'])['Readable_24hrs_before_action_counts'].agg(
        count='sum',     # total action count for this cmid+grade group
        mean='mean',
        median='median',
        min='min',
        max='max'
    ).reset_index()

    # Step 2: Compute total people per grade_group_matched (count of rows, not action counts)
    total_ppl_per_grade_group = hour48_df.groupby('grade_group_matched').size().to_dict()

    # Step 3: Add that to the summary
    summary['grade_group_total_ppl'] = summary['grade_group_matched'].map(total_ppl_per_grade_group)

    return summary
