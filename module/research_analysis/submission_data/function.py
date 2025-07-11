
import pandas as pd

def filter_col_value_userid(df, col=None, value=None, user_id=None):

    filtered_df = df.copy()

    if col is not None and value is not None:
        filtered_df = filtered_df[filtered_df[col] == value]

    if user_id is not None:
        filtered_df = filtered_df[filtered_df['userid'].isin(user_id)]

    return filtered_df

import pandas as pd

def fetch_latest_submittime(df, userid=None, time_col='time'):

    df = df.copy()

    # Normalize userid input to a list if it's a single int
    if userid is not None:
        if isinstance(userid, int):
            userid = [userid]
        df = df[df['userid'].isin(userid)]

    # Sort by time descending so the latest is first
    df = df.sort_values(by=time_col, ascending=False)

    # Drop duplicates: keep only the first (i.e., latest) for each (userid, cmid)
    latest_df = df.drop_duplicates(subset=['userid', 'cmid'], keep='first')

    return latest_df.reset_index(drop=True)


#####TEMP FOR ASSIGN DUE DATE FILE
# Your existing function
def convert_word_time_single(due_date_str, year=2024):

    fixed = due_date_str.lower().strip()

    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    tokens = fixed.split()
    tokens = [t for t in tokens if t not in weekdays]

    cleaned_str = ' '.join(tokens) + f' {year}'
    dt = pd.to_datetime(cleaned_str, errors='coerce')

    if pd.isna(dt):
        raise ValueError(f"Could not parse date string: {due_date_str}")

    return {
        'Readable_Time': dt,
        'Year': dt.year,
        'Month': dt.month,
        'Day': dt.day,
        'Hour': dt.hour,
        'Minute': dt.minute,
        'Second': dt.second
    }

# Step 1: Raw multiline string of names and dates
raw_text = """
Assessment: Research Plan
12 pm Monday 22 January
Assessment: Search and evaluate
12 pm Monday 5 February
Assessment: Referencing quiz
12pm Monday 12 February
Assessment: Data quiz
12pm Monday 19 February
Assessment: Academic writing quiz
12pm Monday 4 March
Assessment: Reflective video
Friday 15 March 5 pm
Assessment 2: Report (40%)
12 pm Monday 11 March
"""

# Step 2: Split into lines, filter out empty lines
lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]

# Step 3: Separate _NAME and DUE_DATE assuming alternating lines: name, date, name, date...
names = lines[0::2]  # even index lines: assessments
dates = lines[1::2]  # odd index lines: due dates

# Step 4: Create initial DataFrame
df = pd.DataFrame({'Name': names, 'DUE_DATE': dates})

# Step 5: Parse DUE_DATE column using your function row-wise
def parse_date(row):
    try:
        return convert_word_time_single(row['DUE_DATE'])
    except ValueError:
        # Handle unparseable dates gracefully
        return {
            'Readable_Time': pd.NaT,
            'Year': None,
            'Month': None,
            'Day': None,
            'Hour': None,
            'Minute': None,
            'Second': None
        }


def merge_assign_and_submissions(assign_duedate, student_submittime, assign_name, assign_cmid):

    # Filter assignment row
    assign_row = assign_duedate[assign_duedate['Name'] == assign_name]

    if assign_row.empty:
        raise ValueError(f"No assignment found with Name '{assign_name}'")

    # Filter student submissions by cmid
    student_rows = student_submittime[student_submittime['cmid'] == assign_cmid]

    if student_rows.empty:
        raise ValueError(f"No student submissions found with cmid '{assign_cmid}'")

    # Rename assign columns by appending _assign_date (except 'Name')
    # assign_rename = {col: f"{col}_assign_date" for col in assign_row.columns if col != 'Name'}
    assign_rename = {col: f"{col}_assign_date" for col in assign_row.columns}
    # assign_rename['Name'] = 'Name'  # Keep assignment name as is
    assign_row_renamed = assign_row.rename(columns=assign_rename)

    # Rename student submission columns by appending _student_submit (except 'userid' and 'cmid')
    student_rename = {col: f"{col}_student_submit" for col in student_rows.columns if col not in ['userid', 'cmid']}
    student_rename['userid'] = 'userid'
    student_rename['cmid'] = 'cmid'
    student_rows_renamed = student_rows.rename(columns=student_rename)

    # Cross join assignment row with student submissions (repeat assign info for each student row)
    # Reset index to merge properly
    assign_row_renamed = assign_row_renamed.reset_index(drop=True)
    student_rows_renamed = student_rows_renamed.reset_index(drop=True)

    # Merge by cross join: assign info repeated for every student row
    combined_df = student_rows_renamed.merge(assign_row_renamed, how='cross')
    keep_col= ['id_student_submit', 'time_student_submit', 'url_student_submit',
       'userid', 'Readable_Time_student_submit', 'Year_student_submit',
       'Month_student_submit', 'Day_student_submit', 'Hour_student_submit',
       'Minute_student_submit', 'Second_student_submit', 'Name_assign_date','Readable_Time_assign_date', 'Year_assign_date',
       'Month_assign_date', 'Day_assign_date', 'Hour_assign_date',
       'Minute_assign_date', 'Second_assign_date']
    combined_df=combined_df[keep_col]

    return combined_df


import pandas as pd
import numpy as np

def summarize_submissions_by_6hour_bins(df):
    # Extract assignment name and due date
    assign_name = df['Name_assign_date'].iloc[0]
    due_date = pd.to_datetime(df['Readable_Time_assign_date'].iloc[0])

    # Convert submission time to datetime
    df = df.copy()  # avoid SettingWithCopyWarning
    df['submission_time'] = pd.to_datetime(df['Readable_Time_student_submit'])

    # Calculate time difference in hours (positive = early, negative = late)
    df['hours_before_due'] = (due_date - df['submission_time']).dt.total_seconds() / 3600

    # Create bins for both early and late submissions in 6-hour intervals
    min_hour = int(np.floor(df['hours_before_due'].min() / 6)) * 6
    max_hour = int(np.ceil(df['hours_before_due'].max() / 6)) * 6
    bin_edges = np.arange(min_hour, max_hour + 6, 6)

    # Create labels for bins
    bin_labels = []
    for h in bin_edges[1:]:  # skip the first edge (left side of first bin)
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

    # Assign time bins
    df['time_bin'] = pd.cut(df['hours_before_due'], bins=bin_edges, labels=bin_labels, right=False)

    # Group and count submissions per bin
    summary_df = df.groupby('time_bin', observed=True).size().reset_index(name='Submission_Count')

    # Print assignment title
    print(f"\nAssignment: {assign_name} (Due: {due_date})\n")
    return summary_df


import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_assign_and_submissions(df):
    assign_name = df['Name_assign_date'].iloc[0]
    due_date = df['Readable_Time_assign_date'].iloc[0]
    submission_times = df['Readable_Time_student_submit']

    fig, ax = plt.subplots(figsize=(14, 4))

    # Plot vertical line for assignment due date
    ax.axvline(due_date, color='red', linestyle='--', label=f'{assign_name} -- Due Date: {due_date}')

    # Plot submissions as scatter on y=1
    ax.scatter(submission_times, [1] * len(submission_times), alpha=0.6, label='Student Submissions')

    # Format x-axis as dates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.tick_params(axis='x', rotation=45)

    # Set x-axis limits with padding
    min_time = min(submission_times.min(), due_date)
    max_time = max(submission_times.max(), due_date)
    delta = (max_time - min_time) / 10
    ax.set_xlim(min_time - delta, max_time + delta)

    ax.set_yticks([])  # Hide y-axis ticks
    ax.set_xlabel('Date and Time')
    ax.set_title(f'{assign_name} -- Due Date: {due_date} and Student Submission Times')
    ax.legend()
    fig.tight_layout()

    return df, fig

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.ticker import MultipleLocator, FuncFormatter

def plot_submission_density_around_due(df):

    due_date = df['Readable_Time_assign_date'].iloc[0]
    submission_times = df['Readable_Time_student_submit']
    time_diff_hours = (submission_times - due_date).dt.total_seconds() / 3600
    total_student = df['userid'].nunique()

    fig, ax = plt.subplots(figsize=(14, 6))

    # Histogram with 6-hour bins
    bin_width = 6
    bins = range(int(np.floor(time_diff_hours.min())) - bin_width, 
                 int(np.ceil(time_diff_hours.max())) + bin_width + 1, bin_width)
    counts, bins_out, patches = ax.hist(
        time_diff_hours, bins=bins,
        color='skyblue', edgecolor='black', label='Submission count'
    )

    # Annotate bar counts
    for count, left_edge in zip(counts, bins):
        if count > 0:
            ax.text(left_edge + bin_width / 2, count + 0.5, f'{int(count)}',
                    ha='center', fontsize=9)

    # KDE plot
    sns.kdeplot(time_diff_hours, color='red', label='Density estimate', ax=ax)

    # Vertical line at due date
    ax.axvline(0, color='red', linestyle='--', label='Due date')

    # Bottom x-axis ticks (hours)
    xticks = np.arange(min(bins), max(bins) + 1, 12)
    ax.set_xticks(xticks)
    ax.tick_params(axis='x', rotation=45)  # Rotate bottom x-axis

    # Top x-axis: Days from due date
    secax = ax.secondary_xaxis('top', functions=(lambda h: h / 24, lambda d: d * 24))
    secax.set_xlabel("Days from Due Date")

    # Formatter for day labels
    def format_days(x, pos):
        if x == 0:
            return "Due"
        elif x > 0:
            return f"{int(x)} day{'s' if x > 1 else ''} late"
        else:
            return f"{int(-x)} day{'s' if x < -1 else ''} early"

    secax.xaxis.set_major_locator(MultipleLocator(1))
    secax.xaxis.set_major_formatter(FuncFormatter(format_days))
    secax.xaxis.set_tick_params(rotation=45)  # Rotate top x-axis

    # Labels and layout
    ax.set_xlabel('Hours from Due Date (Negative = Early, Positive = Late)')
    ax.set_ylabel('Number of Submissions')
    ax.set_title(f'Total {total_student} Student Submissions — Density Around Assignment Due Date')
    ax.legend()
    fig.tight_layout()

    return df, fig


def map_grade_group(combined_submission_df: pd.DataFrame, grade_group_df: pd.DataFrame):

    # Build a mapping from userid to grade_group
    uid_to_group = {}
    for _, row in grade_group_df.iterrows():
        group = row['grade_group']
        for uid in row['userid_list']:
            uid_to_group[uid] = group

    # Copy the time log DF and map
    df = combined_submission_df.copy()
    df['grade_group_matched'] = df['userid'].map(uid_to_group)

    return df

import pandas as pd

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

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

def plot_assign_and_submissions_by_grade(df):
    assign_name = df['Name_assign_date'].iloc[0]
    due_date = df['Readable_Time_assign_date'].iloc[0]
    submission_times = df['Readable_Time_student_submit']
    grade_groups = df['grade_group_matched']

    # Custom order for grades
    grade_order = ['hd', 'cd', 'p', 'f', 'i']

    # Use a distinct palette
    palette = sns.color_palette("Set1", len(grade_order))
    color_map = dict(zip(grade_order, palette))

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(14, 4))

    # Plot vertical line for assignment due date
    ax.axvline(due_date, color='red', linestyle='--', label='Due Date')

    # Plot submissions colored by grade group
    for grade in grade_order:
        group_df = df[df['grade_group_matched'] == grade]
        if not group_df.empty:
            ax.scatter(
                group_df['Readable_Time_student_submit'],
                [1] * len(group_df),
                label=f"{grade.upper()} ({len(group_df)} students)",
                color=color_map[grade],
                alpha=0.7,
                s=40
            )

    # Format x-axis as dates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.setp(ax.get_xticklabels(), rotation=45)

    # X-axis range with padding
    min_time = min(submission_times.min(), due_date)
    max_time = max(submission_times.max(), due_date)
    delta = (max_time - min_time) / 10
    ax.set_xlim(min_time - delta, max_time + delta)

    ax.set_yticks([])  # Hide y-axis ticks
    ax.set_xlabel('Date and Time')
    ax.set_title(f'{assign_name} — Submissions by Grade Group (Due: {due_date.strftime("%Y-%m-%d %H:%M")})')
    ax.legend(title='Grade Group (count)', bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()

    return df, fig





import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

def plot_assign_and_submissions_by_grade_per_user(df):
    assign_name = df['Name_assign_date'].iloc[0]
    due_date = df['Readable_Time_assign_date'].iloc[0]

    grade_order = ['hd', 'cd', 'p', 'f', 'i']
    palette = sns.color_palette("Set1", len(grade_order))
    color_map = dict(zip(grade_order, palette))

    fig, ax = plt.subplots(figsize=(14, 4))

    # Calculate number of unique users per grade group
    users_per_grade = df.groupby('grade_group_matched')['userid'].nunique()

    # For each grade group, plot submissions scaled by submissions per user
    for grade in grade_order:
        group_df = df[df['grade_group_matched'] == grade]
        if group_df.empty:
            continue

        # Count submissions per user in this grade
        subs_per_user = group_df.groupby('userid').size()

        # Map each submission to the normalized size factor
        size_map = subs_per_user / subs_per_user.max()
        sizes = group_df['userid'].map(size_map) * 100  # scale to max size 100

        ax.scatter(
            group_df['Readable_Time_student_submit'],
            [1] * len(group_df),
            s=sizes,
            label=f"{grade.upper()} ({users_per_grade.get(grade, 0)} students)",
            color=color_map[grade],
            alpha=0.7,
            edgecolor='k',
            linewidth=0.5
        )

    # Vertical line for due date
    ax.axvline(due_date, color='red', linestyle='--', label='Due Date')

    # Format x-axis as dates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.tick_params(axis='x', rotation=45)

    # X-axis range with padding
    submission_times = df['Readable_Time_student_submit']
    min_time = min(submission_times.min(), due_date)
    max_time = max(submission_times.max(), due_date)
    delta = (max_time - min_time) / 10
    ax.set_xlim(min_time - delta, max_time + delta)

    ax.set_yticks([])  # Hide y-axis ticks
    ax.set_xlabel('Date and Time')
    ax.set_title(f'{assign_name} — Submissions by Grade Group Due Date: {due_date.strftime("%Y-%m-%d %H:%M")} (Scaled Per User)')
    ax.legend(title='Grade Group (unique users)', bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()

    return df, fig


def plot_submission_density_by_grade(df, grade_col='grade_group_matched'):
    due_date = df['Readable_Time_assign_date'].iloc[0]

    # Make a copy and compute time differences
    df = df.copy()
    df['time_diff_hours'] = (df['Readable_Time_student_submit'] - due_date).dt.total_seconds() / 3600

    total_students = df['userid'].nunique()

    grade_counts = df.groupby(grade_col)['userid'].nunique()

    grade_order = ['hd', 'cd', 'p', 'f', 'i']
    palette = sns.color_palette("Set1", len(grade_order))
    color_map = dict(zip(grade_order, palette))

    sorted_grades = [g for g in grade_order if g in grade_counts.index]

    # Set up the figure
    fig, ax = plt.subplots(figsize=(14, 6))

    bin_width = 6
    min_bin = int(np.floor(df['time_diff_hours'].min() / bin_width)) * bin_width - bin_width
    max_bin = int(np.ceil(df['time_diff_hours'].max() / bin_width)) * bin_width + bin_width
    bins = np.arange(min_bin, max_bin + bin_width, bin_width)

    plot_df = df[df[grade_col].isin(sorted_grades)].copy()

    sns.histplot(
        data=plot_df,
        x='time_diff_hours',
        hue=grade_col,
        bins=bins,
        kde=True,
        palette={g: color_map[g] for g in sorted_grades},
        edgecolor='black',
        alpha=0.6,
        stat='count',
        legend=False,
        ax=ax
    )

    ax.axvline(0, color='red', linestyle='--', label=f'Due date: {due_date.strftime("%Y-%m-%d %H:%M")}')

    xticks = np.arange(min_bin, max_bin + 1, 12)
    ax.set_xticks(xticks)
    ax.tick_params(axis='x', rotation=45)

    # Add secondary x-axis (days from due date)
    secax = ax.secondary_xaxis('top', functions=(lambda h: h / 24, lambda d: d * 24))
    secax.set_xlabel("Days from Due Date")

    def format_days(x, pos):
        if x == 0:
            return "Due"
        elif x > 0:
            return f"{int(x)} day{'s' if x > 1 else ''} late"
        else:
            return f"{int(-x)} day{'s' if x < -1 else ''} early"

    secax.xaxis.set_major_locator(MultipleLocator(1))
    secax.xaxis.set_major_formatter(FuncFormatter(format_days))
    secax.xaxis.set_tick_params(rotation=45)

    ax.set_xlabel('Hours from Due Date (Negative = Early, Positive = Late)')
    ax.set_ylabel('Number of Submissions')
    ax.set_title(f'Total {total_students} Student Submissions by Grade Group — Density Around Assignment Due Date')

    # Custom legend
    handles = []
    labels = []
    for grade in sorted_grades:
        color = color_map[grade]
        count = grade_counts.get(grade, 0)
        handles.append(plt.Line2D([0], [0], marker='o', color=color, linestyle='', markersize=8, alpha=0.6))
        labels.append(f"{grade.upper()} ({count} students)")

    handles.append(plt.Line2D([0], [0], color='red', linestyle='--'))
    labels.append("Due date")

    ax.legend(handles=handles, labels=labels, title='Grade Group', bbox_to_anchor=(1.05, 1), loc='upper left')

    fig.tight_layout()
    
    return df, fig


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import MultipleLocator, FuncFormatter
from scipy.stats import gaussian_kde

def plot_submission_density_by_grade_per_user(df, grade_col='grade_group_matched'):
    due_date = df['Readable_Time_assign_date'].iloc[0]

    df = df.copy()
    df['time_diff_hours'] = (df['Readable_Time_student_submit'] - due_date).dt.total_seconds() / 3600

    total_students = df['userid'].nunique()
    users_per_grade = df.groupby(grade_col)['userid'].nunique()

    grade_order = ['hd', 'cd', 'p', 'f', 'i']
    palette = sns.color_palette("Set1", len(grade_order))
    color_map = dict(zip(grade_order, palette))
    sorted_grades = [g for g in grade_order if g in users_per_grade.index]

    fig, ax = plt.subplots(figsize=(14, 6))

    bin_width = 6
    min_bin = int(np.floor(df['time_diff_hours'].min() / bin_width)) * bin_width - bin_width
    max_bin = int(np.ceil(df['time_diff_hours'].max() / bin_width)) * bin_width + bin_width
    bins = np.arange(min_bin, max_bin + bin_width, bin_width)
    bin_centers = bins[:-1] + bin_width / 2

    max_height = 0
    handles = []
    labels = []

    for grade in sorted_grades:
        group_df = df[df[grade_col] == grade]
        times = group_df['time_diff_hours']
        counts, _ = np.histogram(times, bins=bins)
        count_per_user = counts / users_per_grade[grade]

        ax.bar(bin_centers, count_per_user, width=bin_width * 0.8,
               alpha=0.6, color=color_map[grade], edgecolor='black')

        handles.append(plt.Line2D([0], [0], marker='o', color=color_map[grade],
                                  linestyle='', markersize=8, alpha=0.6))
        labels.append(f"{grade.upper()} ({users_per_grade[grade]} students)")

        if len(times) > 1:
            kde = gaussian_kde(times)
            xs = np.linspace(min_bin, max_bin, 200)
            kde_vals = kde(xs) / users_per_grade[grade]
            ax.plot(xs, kde_vals, color=color_map[grade])

        max_height = max(max_height, count_per_user.max())

    ax.axvline(0, color='red', linestyle='--')
    handles.append(plt.Line2D([0], [0], color='red', linestyle='--'))
    labels.append(f"Due date {due_date.strftime('%Y-%m-%d %H:%M')}")

    xticks = np.arange(min_bin, max_bin + 1, 12)
    ax.set_xticks(xticks)
    ax.tick_params(axis='x', rotation=45)

    secax = ax.secondary_xaxis('top', functions=(lambda h: h / 24, lambda d: d * 24))
    secax.set_xlabel("Days from Due Date")

    def format_days(x, pos):
        if x == 0:
            return "Due"
        elif x > 0:
            return f"{int(x)} day{'s' if x > 1 else ''} late"
        else:
            return f"{int(-x)} day{'s' if x < -1 else ''} early"

    secax.xaxis.set_major_locator(MultipleLocator(1))
    secax.xaxis.set_major_formatter(FuncFormatter(format_days))
    secax.xaxis.set_tick_params(rotation=45)

    ax.set_xlabel('Hours from Due Date (Negative = Early, Positive = Late)')
    ax.set_ylabel('Submissions per User (Normalized)')
    ax.set_title(f'Total {total_students} Student Submissions per User by Grade Group — Density Around Assignment Due Date: {due_date.strftime("%Y-%m-%d %H:%M")}')
    ax.legend(handles=handles, labels=labels, title='Grade Group', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_ylim(0, max_height * 1.2)

    fig.tight_layout()
    return df, fig

