import pandas as pd
import numpy as np
from scipy.stats import linregress
import os

def load_and_filter_access_data(df: pd.DataFrame, week_min=1, week_max=10) -> pd.DataFrame:
    return df[df['study_week'].between(week_min, week_max)].copy()


def compute_weekly_totals(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('study_week')['active_days'].sum().reset_index()


def compute_user_counts(df: pd.DataFrame) -> pd.DataFrame:
    user_counts = df.groupby('study_week')['userid'].nunique().reset_index()
    user_counts.rename(columns={'userid': 'active_users'}, inplace=True)
    user_counts['pct_change'] = user_counts['active_users'].pct_change() * 100
    return user_counts


def compute_user_slope_matrix(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot_table(index='userid', columns='study_week', values='active_days', fill_value=0)
    slopes = []
    for user, row in pivot.iterrows():
        x = row.index.values
        y = row.values
        slope, *_ = linregress(x, y)
        slopes.append({'userid': user, 'slope': slope})
    return pd.DataFrame(slopes)


def categorize_slope(slope, threshold=1.0):
    if slope < -threshold:
        return 'Decreasing'
    elif slope > threshold:
        return 'Increasing'
    return 'Stable'


def detect_30pct_drop_users(df: pd.DataFrame, N=3, threshold=0.3):
    at_risk = []
    for user, group in df.groupby('userid'):
        group = group.sort_values('study_week')
        if len(group) < 2 * N:
            continue
        first_n = group.head(N)['active_days'].mean()
        last_n = group.tail(N)['active_days'].mean()
        if first_n > 0 and (last_n / first_n) <= (1 - threshold):
            at_risk.append({
                'userid': user,
                'first_n_avg': first_n,
                'last_n_avg': last_n,
                'percent_change': 100 * (last_n - first_n) / first_n
            })
    return pd.DataFrame(at_risk)

def preprocess_access_frequency_from_logs(df: pd.DataFrame, term_start_date: str) -> pd.DataFrame:
    df['event_time'] = pd.to_datetime(df['time'], unit='s')
    df['study_week'] = ((df['event_time'] - pd.to_datetime(term_start_date)).dt.days // 7) + 1
    df['event_date'] = df['event_time'].dt.date
    access_df = (
        df.groupby(['userid', 'course', 'study_week'])['event_date']
        .nunique()
        .reset_index(name='active_days')
    )
    return access_df