


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def summarize_final_grades_by_term(df, term_codes):

    print("Unique term codes:")
    print(df['term_code'].unique())

    # Print count of non-null entries in each column
    print("\nCounts of non-null entries in each column:")
    print(df.count())

    # Count and print unique student IDs (userids) per term
    print("\nUnique student count per term code:")
    for term in term_codes:
        unique_student_count = df[df['term_code'] == term]['userid'].nunique()
        print(f"Term_code {term} in course 163601 has {unique_student_count} unique students")


def filter_by_column_value(df, col_name, value):

    return df[df[col_name] == value]


def extract_user_info(df, col_userid, col_username, term_code):

    df=df[df['term_code']== term_code]
    print(df['term_code'].unique())
    print(len(df))
    unique_user_ids = df[col_userid].unique()
    unique_usernames = df[col_username].unique()
    unique_user_count = df[col_userid].nunique()
    
    print(f"Term code = {term_code} having userid includes {unique_user_count} students")
    print(f"Term code = {term_code} having userid includes {unique_user_ids}")
    print(f"Term code = {term_code} having username includes: {unique_usernames}")

    return unique_user_ids, unique_usernames, unique_user_count


def grade_distribution_with_plot(df, term_code):
    # Total enrolment count
    total_enrol = df['userid'].nunique()

    # Define custom grade order
    grade_order = ['HD', 'D', 'C', 'P1', 'P2', 'F1', 'F2', 'I']

    # Count grades
    counts = df['grade'].value_counts()
    ordered_counts = counts.reindex(grade_order, fill_value=0)

    # Create distribution DataFrame
    distribution_df = ordered_counts.reset_index()
    distribution_df.columns = ['Grade', 'Count']

    # Append total enrolment row
    total_row = pd.DataFrame({'Grade': ['Total Enrolment'], 'Count': [total_enrol]})
    distribution_df = pd.concat([distribution_df, total_row], ignore_index=True)

    # ✅ Create figure/axis explicitly (instead of plt.show)
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bar chart (excluding the Total Enrolment row)
    bars = ax.bar(distribution_df['Grade'][:-1], distribution_df['Count'][:-1], color='skyblue')

    # Add counts above bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{int(height)}', ha='center', va='bottom')

    # Titles and labels
    ax.set_title(f"Final Grade Distribution (Term {term_code}, Course 163601)\nTotal Enrolment: {total_enrol}")
    ax.set_xlabel('Grade')
    ax.set_ylabel('Count')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    fig.tight_layout()

    # ✅ Return both DataFrame and Figure
    return distribution_df, fig


### ASSIGN GROUP FINAL GRADES
def assign_grade_group(df: pd.DataFrame) -> pd.DataFrame:
    # Assign grade groups based on grade values
    def map_grade_group(grade):
        if grade == "HD":
            return "hd"
        elif grade in ("D", "C"):
            return "cd"
        elif grade in ("P1", "P2"):
            return "p"
        elif grade in ("F1", "F2"):
            return "f"
        elif grade == "I":
            return "i"
        else:
            return "other"

    df = df.copy()
    df['grade_group'] = df['grade'].apply(map_grade_group)

    # Group by grade_group and aggregate userids, usernames, and count
    grouped = df.groupby('grade_group').agg(
        userid_list=('userid', lambda x: list(x)),
        username_list=('username', lambda x: list(x)),
        group_total=('userid', 'count')
    ).reset_index()

    # Add total enrollment (same for all rows)
    total_enrollment = len(df)
    grouped['total_enrollment'] = total_enrollment
    print(grouped)

    return grouped

def check_uniqueid_in_finalgrade_log(log_df, grade_group_df, term_code, course=None):
    # Extract unique user IDs from log
    unique_userids = log_df['userid'].unique()
    print(f"📌 Unique userids in Term {term_code} Course {course} log:\n{unique_userids}")
    print(f"📊 Number of unique userids: {log_df['userid'].nunique()}")

    # Attempt to show expected total enrollment
    try:
        total_enrol = grade_group_df['total_enrollment'].iloc[0]
        print(f"🎯 Expected total enrollment in final grade data: {total_enrol}")
    except Exception as e:
        print("⚠️ Could not retrieve total enrollment from grade_group_df:", e)

    # Prepare variable names
    course_str = str(course) if course else "none"
    shared_userids_varname = f"userid_inlog_and_finalgrade_term{term_code}_course{course_str}"

    # Combine all userids from grade_group_df into a set
    all_grade_userids = set()
    for user_list in grade_group_df['userid_list']:
        all_grade_userids.update(user_list)

    # Find intersection of userids in log and grade
    userid_inlog_and_finalgrade = list(set(unique_userids) & all_grade_userids)
    globals()[shared_userids_varname] = userid_inlog_and_finalgrade

    # Create DataFrame of shared userids
    userid_inlog_and_finalgrade_df = pd.DataFrame({'userid': userid_inlog_and_finalgrade})

    # Filter log_df for only shared userids
    both_userid_logandgrade_log = log_df[log_df['userid'].isin(userid_inlog_and_finalgrade)]

    # Print summary
    print(f"\n✅ Number of matched userids in both log and grade: {len(userid_inlog_and_finalgrade)}")
    print(f"✅ Number of log records with matched userids: {both_userid_logandgrade_log['userid'].count()}")
    print(f"📋 Shared userids stored in: {shared_userids_varname}")
    # Return both results
    return userid_inlog_and_finalgrade_df, both_userid_logandgrade_log


def process_timestamp_and_split_hours(df, timestamp_col='time'):
    df = df.copy()

    # Convert Unix timestamp (seconds) to datetime
    datetime_col = f"{timestamp_col}_datetime"
    df[datetime_col] = pd.to_datetime(df[timestamp_col], unit='s')

    # Extract year, month, day into new columns
    df[f"{timestamp_col}_year"] = df[datetime_col].dt.year
    df[f"{timestamp_col}_month"] = df[datetime_col].dt.month
    df[f"{timestamp_col}_day"] = df[datetime_col].dt.day

    # Extract hour for time_bucket
    df['access_hour'] = df[datetime_col].dt.hour

    # Create time_bucket column based on access_hour ranges
    conditions = [
        (df['access_hour'] >= 0) & (df['access_hour'] <= 5),
        (df['access_hour'] >= 6) & (df['access_hour'] <= 11),
        (df['access_hour'] >= 12) & (df['access_hour'] <= 17),
        (df['access_hour'] >= 18) & (df['access_hour'] <= 21),
        (df['access_hour'] >= 22) & (df['access_hour'] <= 24),
    ]

    choices = [
        'Early Morning',
        'Morning',
        'Afternoon',
        'Evening',
        'Night (Late)'
    ]

    df['time_bucket'] = np.select(conditions, choices, default='Unknown')

    return df



########### done return dict_df and  dict_fig

def weekly_user_course_timebucket_summary(df, course='', userid=None):
    df = df.copy()

    # Optional: Filter by course if provided
    if course and 'course' in df.columns:
        df = df[df['course'] == course].copy()

    # Optional: Filter by userid if provided
    if userid is not None and 'userid' in df.columns:
        df = df[df['userid'] == userid].copy()

    # Ensure 'time_datetime' is in datetime format
    if 'time_datetime' in df.columns:
        df['time_datetime'] = pd.to_datetime(df['time_datetime'], errors='coerce')
        df = df.dropna(subset=['time_datetime'])
    else:
        raise ValueError("Input DataFrame must contain 'time_datetime' column")

    # Extract ISO calendar year and week separately
    df['year'] = df['time_datetime'].dt.isocalendar().year
    df['week'] = df['time_datetime'].dt.isocalendar().week

    # Map 'time_bucket' to numeric codes
    bucket_map = {
        "Early Morning": 1,
        "Morning": 2,
        "Afternoon": 3,
        "Evening": 4,
        "Night (Late)": 5
    }
    if 'time_bucket' in df.columns:
        df['time_bucket_num'] = df['time_bucket'].map(bucket_map).fillna(0).astype(int)
    else:
        raise ValueError("Input DataFrame must contain 'time_bucket' column")

    # Create readable week range based on year and week
    # Note: to handle week/year correctly, use pandas Timestamp + ISO calendar week formula
    # We use Monday as the first day of the week (ISO standard)
    def get_week_date_range(year, week):
        # ISO weeks start on Monday
        start_date = pd.to_datetime(f'{year}-W{int(week)}-1', format='%G-W%V-%u')
        end_date = start_date + pd.Timedelta(days=6)
        return start_date, end_date

    # Build week range DataFrame
    week_ranges = df[['year', 'week']].drop_duplicates().sort_values(['year', 'week'])
    week_ranges['week_start'], week_ranges['week_end'] = zip(*week_ranges.apply(lambda row: get_week_date_range(row['year'], row['week']), axis=1))
    week_ranges['week_time'] = week_ranges['week_start'].dt.strftime('%Y-%m-%d') + " to " + week_ranges['week_end'].dt.strftime('%Y-%m-%d')

    # Group and count actions by user, year, week, and time_bucket
    grouped = df.groupby(['userid', 'year', 'week', 'time_bucket_num']).size().reset_index(name='action_count')

    # Pivot time buckets to columns
    pivoted = grouped.pivot_table(
        index=['userid', 'year', 'week'],
        columns='time_bucket_num',
        values='action_count',
        fill_value=0
    ).reset_index()

    # Rename bucket columns
    bucket_labels = {
        1: "timebucket_early_morning_action_count",
        2: "timebucket_morning_action_count",
        3: "timebucket_afternoon_action_count",
        4: "timebucket_evening_action_count",
        5: "timebucket_night_late_action_count"
    }
    pivoted = pivoted.rename(columns=bucket_labels)

    # Ensure all expected bucket columns exist
    for col in bucket_labels.values():
        if col not in pivoted.columns:
            pivoted[col] = 0

    # Add total_login column across all timebuckets
    pivoted['total_login'] = pivoted[list(bucket_labels.values())].sum(axis=1)

    # Merge week range info on year and week
    result = pd.merge(pivoted, week_ranges[['year', 'week', 'week_time']], on=['year', 'week'], how='left')

    # Sort for neatness
    result = result.sort_values(['userid', 'year', 'week']).reset_index(drop=True)

    return result



def check_engagement_decline(df, userid=None, threshold=30):

    # Filter by userid if provided
    if userid is not None:
        df = df[df['userid'].isin(userid)]

    # Sort the dataframe to ensure correct week order
    df_sorted = df.sort_values(by=['userid', 'year', 'week','week_time']).copy()

    # Calculate previous week's login using groupby
    df_sorted['prev_total_login'] = df_sorted.groupby('userid')['total_login'].shift(1)

    # Calculate decline percentage
    df_sorted['decline_percentage'] = ((df_sorted['prev_total_login'] - df_sorted['total_login']) /
                                       df_sorted['prev_total_login']) * 100

    # Replace infinite or NaN decline (e.g., first week) with 0
    df_sorted['decline_percentage'] = df_sorted['decline_percentage'].fillna(0).clip(lower=0)

    # Create nudge_activate column
    df_sorted['nudge_activate'] = (df_sorted['decline_percentage'] >= threshold).astype(int)

    # Select relevant columns
    result = df_sorted[['userid', 'year', 'week', 'total_login', 'week_time',
                        'decline_percentage', 'nudge_activate']].reset_index(drop=True)

    return result


def summary_nudge_week(result_df, userid=None):

    # Filter by userid if provided
    if userid is not None:
        result_df = result_df[result_df['userid'].isin(userid)]

    # Helper function to collect readable week info
    def collect_weeks(group, nudge_val):
        subset = group[group['nudge_activate'] == nudge_val]
        return subset[['year', 'week', 'week_time']].apply(
            lambda x: f"{x['year']}-W{x['week']} ({x['week_time']})", axis=1).tolist()

    # Drop the grouping column inside the lambda to avoid DeprecationWarning
    summary = result_df.groupby('userid').apply(
        lambda group: pd.Series({
            'nudge_1_weeks': collect_weeks(group.drop(columns='userid'), 1),
            'nudge_0_weeks': collect_weeks(group.drop(columns='userid'), 0),
            'nudge_1_count': (group['nudge_activate'] == 1).sum(),
            'nudge_0_count': (group['nudge_activate'] == 0).sum()
        })
    ).reset_index()

    return summary



def summary_log_timebucket_plot(df, course='', userid=None):
    # Get summarized weekly data filtered by course and userid
    summary_df = weekly_user_course_timebucket_summary(df, course=course, userid=userid)

    bucket_labels = {
        1: "timebucket_early_morning_action_count",
        2: "timebucket_morning_action_count",
        3: "timebucket_afternoon_action_count",
        4: "timebucket_evening_action_count",
        5: "timebucket_night_late_action_count"
    }
    bucket_cols = list(bucket_labels.values())

    # Add missing columns if any
    for col in bucket_cols:
        if col not in summary_df.columns:
            summary_df[col] = 0

    # Sum total actions per bucket
    bucket_summary = summary_df[bucket_cols].sum().reset_index()
    bucket_summary.columns = ['time_bucket', 'total_action_count']

    # Map bucket order for sorting
    reverse_map = {v: k for k, v in bucket_labels.items()}
    bucket_summary['bucket_order'] = bucket_summary['time_bucket'].map(reverse_map)
    bucket_summary = bucket_summary.sort_values('bucket_order')

    total_count = bucket_summary['total_action_count'].sum()

    # Plot (but do not show)
    fig, ax = plt.subplots(figsize=(10, 6))
    label = userid if userid is not None else "All Users"
    if course:
        label += f", Course: {course}"

    ax.bar(bucket_summary['time_bucket'], bucket_summary['total_action_count'], color='skyblue')
    ax.set_title(f"Total Actions by Time Bucket ({label})")
    ax.set_xlabel("Time of Day")
    ax.set_ylabel("Total Action Count")
    ax.set_xticklabels(bucket_summary['time_bucket'], rotation=45)
    fig.tight_layout()

    # Print total count (optional)
    print(f"\nTotal timebucket action count: {total_count}")

    # Return summary DataFrame and Figure object
    bucket_summary_df = bucket_summary[['bucket_order', 'time_bucket', 'total_action_count']]
    bucket_summary_df = bucket_summary_df.rename(columns={'bucket_order': 'time_bucket_order'})

    return bucket_summary_df, fig

import matplotlib.pyplot as plt

def plot_timebucket_by_week(df, userid=None):
    df = df.copy()

    # Define timebucket columns
    timebuckets = [
        'timebucket_early_morning_action_count',
        'timebucket_morning_action_count',
        'timebucket_afternoon_action_count',
        'timebucket_evening_action_count',
        'timebucket_night_late_action_count'
    ]

    # Optional: filter by user
    if userid is not None:
        df = df[df['userid'] == userid]
        title_user = f"User {userid}"
        summary_df = df.groupby('week_time')[timebuckets].sum().reset_index()
    else:
        title_user = "All Users (Aggregated)"
        summary_df = df.groupby('week_time')[timebuckets].sum().reset_index()

    # Add total login
    summary_df['total_login'] = summary_df[timebuckets].sum(axis=1)

    # Sort by week and set index
    summary_df = summary_df.sort_values(by='week_time')
    summary_df.set_index('week_time', inplace=True)

    # Prepare figure and axis
    fig, ax = plt.subplots(figsize=(14, 6))

    # Plot
    summary_df[timebuckets].plot(
        kind='bar',
        stacked=True,
        ax=ax,
        colormap='tab20c',
        width=0.8,
        edgecolor='black'
    )

    # Add individual segment labels
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2),
                    ha='center',
                    va='center',
                    fontsize=8,
                    color='white'
                )

    # Add total_login labels on top of each bar
    for idx, total in enumerate(summary_df['total_login']):
        ax.annotate(
            f'Total: {int(total)}',
            xy=(idx, total),
            ha='center',
            va='bottom',
            fontsize=9,
            color='black',
            weight='bold',
            xytext=(0, 5),
            textcoords='offset points'
        )

    # Customize plot
    ax.set_title(f"Weekly Login Time Distribution - {title_user}")
    ax.set_ylabel("Login Count")
    ax.set_xlabel("Week")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(title='Time of Day', bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()

    # Return both DataFrame and Figure
    return summary_df.reset_index(), fig



def map_grade_group_to_time_log(time_log_df: pd.DataFrame, grade_group_df: pd.DataFrame):

    # Build a mapping from userid to grade_group
    uid_to_group = {}
    for _, row in grade_group_df.iterrows():
        group = row['grade_group']
        for uid in row['userid_list']:
            uid_to_group[uid] = group

    # Copy the time log DF and map
    df = time_log_df.copy()
    df['grade_group_matched'] = df['userid'].map(uid_to_group)

    return df

#####GROUPBY GRADE GROUPS FUNCTION

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_timebucket_x_stacked_grade(df):
    time_bucket_order = ['early morning', 'morning', 'afternoon', 'evening', 'night late']
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    df = df.copy()
    df['time_bucket'] = df['time_bucket'].str.lower().str.strip()
    df['grade_group_matched'] = df['grade_group_matched'].str.lower().str.strip()

    df = df[df['time_bucket'].isin(time_bucket_order) & df['grade_group_matched'].isin(grade_order)].copy()
    df['time_bucket'] = pd.Categorical(df['time_bucket'], categories=time_bucket_order, ordered=True)
    df['grade_group_matched'] = pd.Categorical(df['grade_group_matched'], categories=grade_order, ordered=True)

    grouped = df.groupby(['time_bucket', 'grade_group_matched'], observed=True).size().reset_index(name='login_count')
    pivot_df = grouped.pivot(index='time_bucket', columns='grade_group_matched', values='login_count').fillna(0)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = sns.color_palette("Set2", n_colors=len(grade_order))
    bottoms = pd.Series([0]*len(pivot_df), index=pivot_df.index)

    for idx, grade in enumerate(grade_order):
        ax.bar(
            pivot_df.index,
            pivot_df[grade],
            bottom=bottoms,
            label=grade.upper(),
            color=colors[idx]
        )
        bottoms += pivot_df[grade]

    for i, tb in enumerate(pivot_df.index):
        cumulative_height = 0
        for grade in grade_order:
            height = pivot_df.loc[tb, grade]
            if height > 0:
                ax.text(
                    i, cumulative_height + height / 2,
                    int(height),
                    ha='center', va='center',
                    fontsize=9,
                    color='black'
                )
                cumulative_height += height

    ax.set_title("Login Counts by Time Bucket (x-axis) Stacked by Grade Group", fontsize=16)
    ax.set_xlabel("Time Bucket", fontsize=14)
    ax.set_ylabel("Login Count", fontsize=14)
    ax.set_xticks(range(len(pivot_df)))
    ax.set_xticklabels(pivot_df.index, rotation=25)
    ax.legend(title="Grade Group", fontsize=12, title_fontsize=13, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout()

    return pivot_df.reset_index(), fig


def plot_normalized_timebucket_x_stacked_grade(raw_df: pd.DataFrame, gradegroup_df: pd.DataFrame):
    time_bucket_order = ['early morning', 'morning', 'afternoon', 'evening', 'night late']
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    df_long = raw_df.melt(id_vars='time_bucket', value_vars=grade_order,
                          var_name='grade_group_matched', value_name='count')

    df_long['time_bucket'] = df_long['time_bucket'].str.lower().str.strip()
    df_long['grade_group_matched'] = df_long['grade_group_matched'].str.lower().str.strip()
    df_long = df_long[
        df_long['time_bucket'].isin(time_bucket_order) &
        df_long['grade_group_matched'].isin(grade_order)
    ]

    df_long['time_bucket'] = pd.Categorical(df_long['time_bucket'], categories=time_bucket_order, ordered=True)
    df_long['grade_group_matched'] = pd.Categorical(df_long['grade_group_matched'], categories=grade_order, ordered=True)

    group_sizes = gradegroup_df[['grade_group', 'group_total']].copy()
    group_sizes.columns = ['grade_group_matched', 'group_total']

    df_merged = df_long.merge(group_sizes, on='grade_group_matched', how='left')
    df_merged['count_per_user'] = (df_merged['count'] / df_merged['group_total']).round(2)

    pivot_df = df_merged.pivot(index='time_bucket', columns='grade_group_matched', values='count_per_user').fillna(0)
    pivot_df = pivot_df.reindex(index=time_bucket_order, columns=grade_order, fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = sns.color_palette("Set2", n_colors=len(grade_order))
    bottoms = pd.Series([0] * len(pivot_df), index=pivot_df.index)

    for idx, grade in enumerate(grade_order):
        heights = pivot_df[grade]
        ax.bar(
            pivot_df.index,
            heights,
            bottom=bottoms,
            label=grade.upper(),
            color=colors[idx]
        )
        bottoms += heights

    for i, tb in enumerate(pivot_df.index):
        cumulative_height = 0
        for grade in grade_order:
            h = pivot_df.loc[tb, grade]
            if h > 0:
                ax.text(
                    i, cumulative_height + h / 2,
                    f"{h:.1f}",
                    ha='center', va='center',
                    fontsize=9,
                    color='black'
                )
                cumulative_height += h

    ax.set_title("Per-User Login Distribution by Time Bucket (Stacked by Grade Group)", fontsize=16)
    ax.set_xlabel("Time Bucket", fontsize=14)
    ax.set_ylabel("Logins per User", fontsize=14)
    ax.set_xticks(range(len(pivot_df)))
    ax.set_xticklabels(pivot_df.index, rotation=25)
    ax.legend(title="Grade Group", fontsize=12, title_fontsize=13, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout()

    return pivot_df.reset_index(), fig

def plot_weekly_timebucket_stacked_by_grade(df):
    time_bucket_order = ['early morning', 'morning', 'afternoon', 'evening', 'night late']
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    df = df.copy()
    df['time_bucket'] = df['time_bucket'].str.lower().str.strip()
    df['grade_group_matched'] = df['grade_group_matched'].str.lower().str.strip()
    df['time_datetime'] = pd.to_datetime(df['time_datetime'])

    df['week_start'] = df['time_datetime'] - pd.to_timedelta(df['time_datetime'].dt.weekday, unit='d')
    df['week_end'] = df['week_start'] + pd.Timedelta(days=6)
    df['week_range'] = df['week_start'].dt.strftime('%Y-%m-%d') + ' to ' + df['week_end'].dt.strftime('%Y-%m-%d')

    df = df[df['time_bucket'].isin(time_bucket_order) & df['grade_group_matched'].isin(grade_order)].copy()
    df['time_bucket'] = pd.Categorical(df['time_bucket'], categories=time_bucket_order, ordered=True)
    df['grade_group_matched'] = pd.Categorical(df['grade_group_matched'], categories=grade_order, ordered=True)

    grouped = df.groupby(['week_range', 'time_bucket', 'grade_group_matched'], observed=True).size().reset_index(name='count')

    pivot_df = grouped.pivot_table(
        index=['week_range', 'time_bucket'],
        columns='grade_group_matched',
        values='count',
        fill_value=0
    ).reset_index()

    pivot_df['week_sort'] = pd.to_datetime(pivot_df['week_range'].str[:10])
    pivot_df = pivot_df.sort_values(['week_sort', 'time_bucket'])

    fig, ax = plt.subplots(figsize=(18, 8))
    colors = sns.color_palette("Set2", len(grade_order))
    x = range(len(pivot_df))
    bottom = [0] * len(pivot_df)

    for idx, grade in enumerate(grade_order):
        ax.bar(
            x,
            pivot_df[grade],
            bottom=bottom,
            color=colors[idx],
            label=grade.upper()
        )
        bottom = [i + j for i, j in zip(bottom, pivot_df[grade])]

    for i in x:
        height = 0
        for grade in grade_order:
            value = pivot_df.loc[i, grade]
            if value > 0:
                ax.text(i, height + value / 2, int(value), ha='center', va='center', fontsize=9)
                height += value

    pivot_df['xtick'] = pivot_df['week_range'] + "\n" + pivot_df['time_bucket'].str.title()
    ax.set_xticks(x)
    ax.set_xticklabels(pivot_df['xtick'], rotation=45, ha='right')

    ax.set_title("Weekly Time Bucket Logins Stacked by Grade Group", fontsize=16)
    ax.set_xlabel("Week Range and Time Bucket", fontsize=13)
    ax.set_ylabel("Login Count", fontsize=13)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.legend(title='Grade Group', loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=10)
    fig.tight_layout()

    return pivot_df, fig

import matplotlib.pyplot as plt
import seaborn as sns

def generate_daily_timebucket_by_grade(df):
    # Ensure datetime column is in correct format
    df['time_datetime'] = pd.to_datetime(df['time_datetime'])

    # Extract date
    df['date'] = df['time_datetime'].dt.date

    # Normalize time_bucket and grade_group
    df['time_bucket'] = df['time_bucket'].str.lower().str.strip()
    df['grade_group_matched'] = df['grade_group_matched'].str.lower().str.strip()

    # Map time buckets to numbers for pivoting
    bucket_map = {
        "early morning": 1,
        "morning": 2,
        "afternoon": 3,
        "evening": 4,
        "night late": 5
    }

    df['time_bucket_num'] = df['time_bucket'].map(bucket_map).fillna(0).astype(int)

    # Group by grade group, date, and time bucket
    grouped = df.groupby(['grade_group_matched', 'date', 'time_bucket_num']).size().reset_index(name='action_count')

    # Pivot table: rows = (grade_group, date), columns = time buckets
    pivoted = grouped.pivot_table(
        index=['grade_group_matched', 'date'],
        columns='time_bucket_num',
        values='action_count',
        fill_value=0
    ).reset_index()

    # Rename time bucket columns
    bucket_labels = {
        1: "timebucket_early_morning_action_count",
        2: "timebucket_morning_action_count",
        3: "timebucket_afternoon_action_count",
        4: "timebucket_evening_action_count",
        5: "timebucket_night_late_action_count"
    }
    pivoted = pivoted.rename(columns=bucket_labels)

    # Ensure all expected columns exist
    for col in bucket_labels.values():
        if col not in pivoted.columns:
            pivoted[col] = 0

    # Reorder columns
    final_columns = ['grade_group_matched', 'date'] + list(bucket_labels.values())
    daily_summary_df = pivoted[final_columns]

    ### 🔍 PLOTTING
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.set(style='whitegrid')

    # Aggregate across grade groups for total counts
    total_counts = daily_summary_df.groupby('date')[
        list(bucket_labels.values())
    ].sum().reset_index()

    # Stacked bar plot
    bottom = np.zeros(len(total_counts))
    colors = sns.color_palette("Set2", len(bucket_labels))
    for i, col in enumerate(bucket_labels.values()):
        ax.bar(
            total_counts['date'],
            total_counts[col],
            bottom=bottom,
            label=col.replace("timebucket_", "").replace("_action_count", "").replace("_", " ").title(),
            color=colors[i]
        )
        bottom += total_counts[col].values

    ax.set_title("Daily Login Distribution by Time Bucket", fontsize=16)
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Actions")
    ax.legend(title="Time Bucket", bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()

    ### ✅ Return DataFrame and Figure
    return daily_summary_df, fig



### DAILY SUMMARY IN WEEK
def daily_summary_log_timebucket_plot(df: pd.DataFrame):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])

    bucket_labels = {
        "timebucket_early_morning_action_count": "Early Morning",
        "timebucket_morning_action_count": "Morning",
        "timebucket_afternoon_action_count": "Afternoon",
        "timebucket_evening_action_count": "Evening",
        "timebucket_night_late_action_count": "Late Night"
    }

    melted_df = df.melt(
        id_vars=['date'],
        value_vars=list(bucket_labels.keys()),
        var_name='time_bucket',
        value_name='action_count'
    )
    melted_df['time_bucket_label'] = melted_df['time_bucket'].map(bucket_labels)
    melted_df['action_count'] = melted_df['action_count'].fillna(0)
    melted_df['weekday'] = melted_df['date'].dt.strftime('%a')
    melted_df['week_start'] = melted_df['date'] - pd.to_timedelta(melted_df['date'].dt.weekday, unit='D')

    total_action_count = melted_df['action_count'].sum()

    figs = []
    # Plot one figure per week
    for week_start, group in melted_df.groupby('week_start'):
        fig, ax = plt.subplots(figsize=(16, 6))
        sns.barplot(
            data=group,
            x='weekday',
            y='action_count',
            hue='time_bucket_label',
            estimator='sum',
            palette='Set2',
            dodge=True,
            order=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            ax=ax
        )

        sns.despine(left=True, bottom=True)
        ax.grid(False)

        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', label_type='center', fontsize=9, padding=1, color='black')

        week_end = week_start + pd.Timedelta(days=6)
        week_label = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
        ax.set_title(f'Weekly Time Bucket Action Counts: Week of {week_label}', fontsize=14)
        ax.set_xlabel('Day of Week', fontsize=12)
        ax.set_ylabel('Total Action Count', fontsize=12)
        ax.legend(title='Time Bucket')
        fig.tight_layout()

        figs.append((week_label, fig))
    
        # Instead of print, return total count info as well
    return melted_df, figs, int(total_action_count)
  
    # fig_dict = {week_label: fig for week_label, fig in figs}
    # return melted_df, fig_dict, int(total_action_count)




def plot_weekday_timebucket_grade_distribution(df: pd.DataFrame):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['weekday'] = df['date'].dt.day_name().str[:3]

    df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='D')
    df['week_end'] = df['week_start'] + pd.Timedelta(days=6)
    df['week_label'] = df['week_start'].dt.strftime('%Y-%m-%d') + ' to ' + df['week_end'].dt.strftime('%Y-%m-%d')

    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    bucket_cols = {
        "timebucket_early_morning_action_count": "Early Morning",
        "timebucket_morning_action_count": "Morning",
        "timebucket_afternoon_action_count": "Afternoon",
        "timebucket_evening_action_count": "Evening",
        "timebucket_night_late_action_count": "Night Late"
    }
    bucket_order = list(bucket_cols.values())
    grade_order = ['hd','cd','p','f','i']

    melted = df.melt(
        id_vars=['grade_group_matched','week_label','weekday'],
        value_vars=list(bucket_cols.keys()),
        var_name='bucket_col',
        value_name='count'
    )
    melted['time_bucket'] = melted['bucket_col'].map(bucket_cols)
    melted = melted[melted['grade_group_matched'].isin(grade_order)]
    melted['grade_group_matched'] = pd.Categorical(melted['grade_group_matched'], categories=grade_order, ordered=True)
    melted = melted[melted['weekday'].isin(day_order)]

    grade_colors = sns.color_palette("Set2", len(grade_order))
    day_colors = sns.color_palette("tab10", len(day_order))
    day_color_map = dict(zip(day_order, day_colors))

    figs = []
    for week, week_df in melted.groupby('week_label'):
        x_labels = [f"{day} {bucket}" for day in day_order for bucket in bucket_order]
        data = pd.DataFrame(0, index=x_labels, columns=grade_order)
        for _, row in week_df.iterrows():
            key = f"{row['weekday']} {row['time_bucket']}"
            data.at[key, row['grade_group_matched']] += row['count']

        fig, ax = plt.subplots(figsize=(18, 6))
        bottoms = [0] * len(data)
        x = range(len(data))
        for i, grade in enumerate(grade_order):
            heights = data[grade].values
            ax.bar(
                x, heights,
                bottom=bottoms,
                color=grade_colors[i],
                label=grade.upper(),
                width=0.8
            )
            bottoms = [bottoms[j] + heights[j] for j in range(len(heights))]

        for idx in x:
            cum = 0
            for grade in grade_order:
                h = data.iloc[idx][grade]
                if h > 0:
                    ax.text(
                        idx, cum + h/2, int(h),
                        ha='center', va='center',
                        fontsize=8, color='white'
                    )
                    cum += h

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right')
        for label in ax.get_xticklabels():
            day = label.get_text().split(' ',1)[0]
            label.set_color(day_color_map.get(day, 'black'))

        ax.set_xlabel('Day and Time Bucket')
        ax.set_ylabel('Login Count')
        ax.set_title(f"Week {week} – Login Distribution by Grade and Time Bucket")
        ax.legend(title='Grade Group', bbox_to_anchor=(1.01, 1), loc='upper left')
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        fig.tight_layout()

        figs.append((week, fig))

    return melted, figs

def normalize_action_with_group_info(action_df: pd.DataFrame, gradegroup_df: pd.DataFrame) -> pd.DataFrame:

    # Step 1: Drop missing values in count
    action_df=pd.DataFrame(action_df)
    df_clean = action_df.dropna(subset=['count']).copy()

    # Step 2: Extract only relevant columns from gradegroup_df
    group_sizes = gradegroup_df[['grade_group', 'group_total']].copy()

    # Step 3: Merge group sizes into action log
    df_merged = df_clean.merge(group_sizes, left_on='grade_group_matched', right_on='grade_group', how='left')

    # Step 4: Remove rows where group size is missing or zero
    df_merged = df_merged.dropna(subset=['group_total'])
    df_merged = df_merged[df_merged['group_total'] > 0]

    # Step 5: Normalize count
    df_merged['count_per_user'] = df_merged['count'] / df_merged['group_total']
    df_merged['count_per_100_users'] = df_merged['count_per_user'] * 100

    # Round for readability
    df_merged['count_per_user'] = df_merged['count_per_user'].round(2)
    df_merged['count_per_100_users'] = df_merged['count_per_100_users'].round(2)

    # Step 6: Clean up (optional)
    df_merged.drop(columns=['grade_group'], inplace=True)

    return df_merged



# def plot_weekday_timebucket_grade_distribution_per_user(df: pd.DataFrame):
    import seaborn as sns
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    bucket_order = ["Early Morning", "Morning", "Afternoon", "Evening", "Night Late"]
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    df = df.copy()
    df = df[df['grade_group_matched'].isin(grade_order)]
    df = df[df['weekday'].isin(day_order)]
    df['grade_group_matched'] = pd.Categorical(df['grade_group_matched'], categories=grade_order, ordered=True)
    df['weekday'] = pd.Categorical(df['weekday'], categories=day_order, ordered=True)
    df['time_bucket'] = pd.Categorical(df['time_bucket'], categories=bucket_order, ordered=True)

    grade_colors = sns.color_palette("Set2", len(grade_order))
    day_colors = sns.color_palette("tab10", len(day_order))
    day_color_map = dict(zip(day_order, day_colors))

    figs = []
    for week, week_df in df.groupby('week_label'):
        x_labels = [f"{day} {bucket}" for day in day_order for bucket in bucket_order]
        x = range(len(x_labels))
        data = pd.DataFrame(0.0, index=x_labels, columns=grade_order)

        for _, row in week_df.iterrows():
            key = f"{row['weekday']} {row['time_bucket']}"
            data.at[key, row['grade_group_matched']] += row['count_per_user']

        fig, ax = plt.subplots(figsize=(18, 6))
        bottoms = [0] * len(data)
        for i, grade in enumerate(grade_order):
            heights = data[grade].values
            ax.bar(
                x, heights,
                bottom=bottoms,
                color=grade_colors[i],
                label=grade.upper(),
                width=0.8
            )
            bottoms = [bottoms[j] + heights[j] for j in range(len(heights))]

        for idx in x:
            cum = 0
            for grade in grade_order:
                h = data.iloc[idx][grade]
                if h > 0:
                    ax.text(
                        idx, cum + h / 2, f"{h:.1f}",
                        ha='center', va='center',
                        fontsize=8, color='white'
                    )
                    cum += h

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right')
        for label in ax.get_xticklabels():
            day = label.get_text().split(' ')[0]
            label.set_color(day_color_map.get(day, 'black'))

        ax.set_xlabel('Day and Time Bucket')
        ax.set_ylabel('Actions per User')
        ax.set_title(f"Week {week} – Login Distribution per User by Grade and Time Bucket")
        ax.legend(title='Grade Group', bbox_to_anchor=(1.01, 1), loc='upper left')
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        fig.tight_layout()

        figs.append((f"week_{week}", fig))  # ✅ Tuple of (name, fig)

    return df, figs

# def plot_weekday_timebucket_grade_distribution_per_user(df: pd.DataFrame):
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    bucket_order = ["Early Morning", "Morning", "Afternoon", "Evening", "Night Late"]
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    df = df.copy()
    df = df[df['grade_group_matched'].isin(grade_order)]
    df = df[df['weekday'].isin(day_order)]
    df['grade_group_matched'] = pd.Categorical(df['grade_group_matched'], categories=grade_order, ordered=True)
    df['weekday'] = pd.Categorical(df['weekday'], categories=day_order, ordered=True)
    df['time_bucket'] = pd.Categorical(df['time_bucket'], categories=bucket_order, ordered=True)

    grade_colors = sns.color_palette("Set2", len(grade_order))
    day_colors = sns.color_palette("tab10", len(day_order))
    day_color_map = dict(zip(day_order, day_colors))

    figs = []
    for week, week_df in df.groupby('week_label'):
        x_labels = [f"{day} {bucket}" for day in day_order for bucket in bucket_order]
        x = range(len(x_labels))
        data = pd.DataFrame(0.0, index=x_labels, columns=grade_order)

        for _, row in week_df.iterrows():
            key = f"{row['weekday']} {row['time_bucket']}"
            data.at[key, row['grade_group_matched']] += row['count_per_user']

        fig, ax = plt.subplots(figsize=(18, 6))
        bottoms = [0] * len(data)
        for i, grade in enumerate(grade_order):
            heights = data[grade].values
            ax.bar(
                x, heights,
                bottom=bottoms,
                color=grade_colors[i],
                label=grade.upper(),
                width=0.8
            )
            bottoms = [bottoms[j] + heights[j] for j in range(len(heights))]

        for idx in x:
            cum = 0
            for grade in grade_order:
                h = data.iloc[idx][grade]
                if h > 0:
                    ax.text(
                        idx, cum + h / 2, f"{h:.1f}",
                        ha='center', va='center',
                        fontsize=8, color='white'
                    )
                    cum += h

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right')
        for label in ax.get_xticklabels():
            day = label.get_text().split(' ')[0]
            label.set_color(day_color_map.get(day, 'black'))

        ax.set_xlabel('Day and Time Bucket')
        ax.set_ylabel('Actions per User')
        ax.set_title(f"Week {week} – Login Distribution per User by Grade and Time Bucket")
        ax.legend(title='Grade Group', bbox_to_anchor=(1.01, 1), loc='upper left')
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        fig.tight_layout()

        figs.append((week, fig))

    return df, figs

def plot_weekday_timebucket_grade_distribution_per_user(df: pd.DataFrame):
    import seaborn as sns
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    bucket_order = ["Early Morning", "Morning", "Afternoon", "Evening", "Night Late"]
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    df = df.copy()
    df = df[df['grade_group_matched'].isin(grade_order)]
    df = df[df['weekday'].isin(day_order)]
    df['grade_group_matched'] = pd.Categorical(df['grade_group_matched'], categories=grade_order, ordered=True)
    df['weekday'] = pd.Categorical(df['weekday'], categories=day_order, ordered=True)
    df['time_bucket'] = pd.Categorical(df['time_bucket'], categories=bucket_order, ordered=True)

    grade_colors = sns.color_palette("Set2", len(grade_order))
    day_colors = sns.color_palette("tab10", len(day_order))
    day_color_map = dict(zip(day_order, day_colors))

    figs = []
    for week, week_df in df.groupby('week_label'):
        x_labels = [f"{day} {bucket}" for day in day_order for bucket in bucket_order]
        x = range(len(x_labels))
        data = pd.DataFrame(0.0, index=x_labels, columns=grade_order)

        for _, row in week_df.iterrows():
            key = f"{row['weekday']} {row['time_bucket']}"
            data.at[key, row['grade_group_matched']] += row['count_per_user']

        fig, ax = plt.subplots(figsize=(18, 6))
        bottoms = [0] * len(data)
        for i, grade in enumerate(grade_order):
            heights = data[grade].values
            ax.bar(
                x, heights,
                bottom=bottoms,
                color=grade_colors[i],
                label=grade.upper(),
                width=0.8
            )
            bottoms = [bottoms[j] + heights[j] for j in range(len(heights))]

        for idx in x:
            cum = 0
            for grade in grade_order:
                h = data.iloc[idx][grade]
                if h > 0:
                    ax.text(
                        idx, cum + h / 2, f"{h:.1f}",
                        ha='center', va='center',
                        fontsize=8, color='white'
                    )
                    cum += h

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right')
        for label in ax.get_xticklabels():
            day = label.get_text().split(' ')[0]
            label.set_color(day_color_map.get(day, 'black'))

        ax.set_xlabel('Day and Time Bucket')
        ax.set_ylabel('Actions per User')
        ax.set_title(f"Week {week} – Login Distribution per User by Grade and Time Bucket")
        ax.legend(title='Grade Group', bbox_to_anchor=(1.01, 1), loc='upper left')
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        fig.tight_layout()

        figs.append((f"week_{week}", fig))  # ✅ Tuple of (name, fig)

    return df, figs
