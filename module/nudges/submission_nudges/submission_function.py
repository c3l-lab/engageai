############################################# Moodle API  ######################################################################################## 

def moodle_attach_assign_duedate(df_assign_duedate, df_submissions):


    if df_assign_duedate.empty:
        raise ValueError("df_assign_duedate is empty. No due date found.")

    # If more than one assignment row, pick the latest due date
    if len(df_assign_duedate) > 1:
        print("[Warning] More than one due date found. Taking the latest one.")
        assign_duetime_df = df_assign_duedate.sort_values("due_date", ascending=False).iloc[:1]
    else:
        assign_duetime_df = df_assign_duedate

    # Rename columns only just before concat
    assign_duetime_df_renamed = assign_duetime_df.rename(
        columns=lambda col: f"{col}_assign_duedate"
    )

    # Repeat the single-row DataFrame to match the number of submission rows
    assign_duetime_expanded = pd.concat(
        [assign_duetime_df_renamed] * len(df_submissions), ignore_index=True
    )

    # Reset index of df_submissions for alignment
    df_submissions = df_submissions.reset_index(drop=True)

    # Concatenate side-by-side
    merged_df = pd.concat([df_submissions, assign_duetime_expanded], axis=1)

    return merged_df


def moodle_calculate_time_and_score(df, T_max=14, T_late=-2):
    df = df.copy()

    # Convert to datetime
    df['due_date_assign_duedate'] = pd.to_datetime(df['due_date_assign_duedate'])
    df['timemodified_readable'] = pd.to_datetime(df['timemodified_readable'])

    # Compute time differences
    time_diff = df['due_date_assign_duedate'] - df['timemodified_readable']
    print(time_diff)
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

def moodle_sum_early_late_counts(df):
    df = df.copy()

    # Create time category
    df["time_category"] = df["time_before_deadline_hours"].apply(
        lambda x: "early" if x > 0 else "late"
    )

    # Count submissions by time category
    count_summary = (
        df.groupby("time_category", observed=True)
        .size()
        .reset_index(name="submission_count")
    )

    # Pivot to get early and late counts as columns
    final_df = (
        count_summary.pivot_table(index=None,
                                  columns="time_category",
                                  values="submission_count",
                                  fill_value=0)
        .rename(columns={"early": "early_count", "late": "late_count"})
        .reset_index(drop=True)
    )

    # Ensure both columns exist even if data has only one category
    for col in ["early_count", "late_count"]:
        if col not in final_df.columns:
            final_df[col] = 0

    return final_df




############################################# Reserach Analysis from Azure Download Data ######################################################################################## 

import pandas as pd

def attach_assign_duedate(submission_df, assign_duetime_df):
    # Rename all columns in assign_duetime_df to end with "_assign_duedate"
    assign_duetime_df_renamed = assign_duetime_df.rename(
        columns=lambda col: f"{col}_assign_duedate"
    )

    # Repeat assign_duetime_df for each row in submission_df (if just 1 assignment)
    if len(assign_duetime_df_renamed) == 1:
        assign_duetime_expanded = pd.concat([assign_duetime_df_renamed] * len(submission_df), ignore_index=True)
    else:
        raise ValueError("assign_duetime_df should have exactly one row for broadcasting.")

    # Concatenate side-by-side
    merged_df = pd.concat([submission_df.reset_index(drop=True), assign_duetime_expanded], axis=1)
    return merged_df

def calculate_time_and_score(df, T_max=14, T_late=-2):
    df = df.copy()

    # Convert to datetime
    df['Readable_Time_student_submit'] = pd.to_datetime(df['Readable_Time_student_submit'])
    df['Readable_Time_assign_date'] = pd.to_datetime(df['Readable_Time_assign_date'])

    # Compute time differences
    time_diff = df['Readable_Time_assign_date'] - df['Readable_Time_student_submit']
    print(time_diff)
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

def summarize_submission_scores(df):

    # Overall summary (as a single-row DataFrame)
    overall_summary = pd.DataFrame({
        'avg_submission_score': [df['submission_score'].mean()],
        'median_submission_score': [df['submission_score'].median()],
        'max_submission_score': [df['submission_score'].max()],
        'min_submission_score': [df['submission_score'].min()]

    })

    # # Grouped by userid (max and min per user)
    # user_summary = df.groupby('userid')['submission_score'].agg(
    #     max_submission_score='max',
    #     min_submission_score='min'
    # ).reset_index()

    # Grouped by grade_group_matched (avg, max, min)
    grade_summary = df.groupby('grade_group_matched')['submission_score'].agg(
        avg_submission_score='mean',
        median_submission_score='median',
        max_submission_score='max',
        min_submission_score='min'
    ).reset_index()

    return overall_summary, grade_summary

############################################### Grade Group ####################################################################################################

import pandas as pd
import numpy as np

def summarize_submissions_by_bins_grade_group(df, bin_hours=6):
    assign_name = df['Name_assign_date'].iloc[0]
    due_date = pd.to_datetime(df['Readable_Time_assign_date'].iloc[0])

    df = df.copy()
    df['submission_time'] = pd.to_datetime(df['Readable_Time_student_submit'])
    df['hours_before_due'] = (due_date - df['submission_time']).dt.total_seconds() / 3600

    # Define bins with custom bin size
    min_hour = int(np.floor(df['hours_before_due'].min() / bin_hours)) * bin_hours
    max_hour = int(np.ceil(df['hours_before_due'].max() / bin_hours)) * bin_hours
    bin_edges = np.arange(min_hour, max_hour + bin_hours, bin_hours)

    bin_labels = []
    for h in bin_edges[1:]:
        if h >= 0:
            days = int(h // 24)
            hours = int(h % 24)
            label = f"{days}d {hours}h early" if days > 0 else f"{hours}h early"
        else:
            h_abs = abs(h)
            days = int(h_abs // 24)
            hours = int(h_abs % 24)
            label = f"{days}d {hours}h late" if days > 0 else f"{hours}h late"
        bin_labels.append(label)

    df['time_bin'] = pd.cut(df['hours_before_due'], bins=bin_edges, labels=bin_labels, right=False)

    # Set custom order for grade groups
    grade_order = ['hd', 'cd', 'p', 'f', 'i']
    df['grade_group_matched'] = pd.Categorical(df['grade_group_matched'], categories=grade_order, ordered=True)

    # Group by grade and bin to count submissions
    summary_df = (
        df.groupby(['grade_group_matched', 'time_bin'], observed=True)
        .size()
        .reset_index(name='Submission_Count')
    )

    # Add total submissions per grade group
    total_per_grade = (
        df.groupby('grade_group_matched', observed=True)
        .size()
        .reset_index(name='total_grade_group')
    )

    # Merge total counts into the summary
    summary_df = summary_df.merge(total_per_grade, on='grade_group_matched', how='left')

    # Sort by grade and bin
    summary_df = summary_df.sort_values(['grade_group_matched', 'time_bin'])

    print(f"\nAssignment: {assign_name} (Due: {due_date})\nBin size: {bin_hours} hours\n")
    return summary_df

def summarize_early_late_counts(summary_by_grade):
    # Ensure proper category order for grade group
    grade_order = ['hd', 'cd', 'p', 'f', 'i']
    summary_by_grade = summary_by_grade.copy()
    summary_by_grade['grade_group_matched'] = pd.Categorical(
        summary_by_grade['grade_group_matched'],
        categories=grade_order,
        ordered=True
    )

    # Add 'time_category' column: 'early' or 'late'
    summary_by_grade['time_category'] = summary_by_grade['time_bin'].apply(
        lambda x: 'early' if 'early' in str(x) else 'late'
    )

    # Group by grade and time_category to get early/late counts
    grouped = (
        summary_by_grade
        .groupby(['grade_group_matched', 'time_category'], observed=True)['Submission_Count']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={'early': 'early_count', 'late': 'late_count'})
    )

    # Get total_grade_group per grade (same as in summary_by_grade)
    total_counts = (
        summary_by_grade.groupby('grade_group_matched', observed=True)['total_grade_group']
        .max()
        .reset_index()
    )

    # Merge total counts into grouped summary
    final_df = grouped.merge(total_counts, on='grade_group_matched', how='left')

    # Ensure expected columns are present
    for col in ['early_count', 'late_count']:
        if col not in final_df.columns:
            final_df[col] = 0

    return final_df.sort_values('grade_group_matched')

