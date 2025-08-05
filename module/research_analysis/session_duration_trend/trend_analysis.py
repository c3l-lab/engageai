import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# Define time bucket function for sessions and forum activities
def time_bucket(hour):
    if 0 <= hour <= 5:
        return 'Early Morning'
    elif 6 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 17:
        return 'Afternoon'
    elif 18 <= hour <= 21:
        return 'Evening'
    else:
        return 'Night (Late)'

class TrendAnalyzer:
    def __init__(self, session_df, pre_aggregated=False):
        self.df = session_df.copy()
        if not pre_aggregated:
            self._prepare()
        if 'study_week' in self.df.columns:
            self.df = self.df[self.df['study_week'].between(1, 10)]

    def _prepare(self):
        if not pd.api.types.is_datetime64_any_dtype(self.df['min']):
            self.df['min'] = pd.to_datetime(self.df['min'])
        if not pd.api.types.is_datetime64_any_dtype(self.df['max']):
            self.df['max'] = pd.to_datetime(self.df['max'])

        self.df['session_start'] = self.df['min']
        self.df['session_end'] = self.df['max']
        self.df['session_duration'] = self.df['session_duration'].astype(float)
        self.df['study_week'] = self.df['session_start'].dt.isocalendar().week

    def avg_session_duration_per_week(self):
        return self.df.groupby('study_week')['session_duration'].mean().reset_index()

    def session_count_per_week(self):
        return self.df.groupby('study_week')['session_id'].count().reset_index(name='num_sessions')

    def active_users_per_week(self):
        return self.df.groupby('study_week')['userid'].nunique().reset_index(name='active_users')

    def session_duration_distribution(self, bins=None):
        self.df['duration_bin'] = pd.cut(self.df['session_duration'], bins=bins)
        return self.df['duration_bin'].value_counts().sort_index().reset_index(name='count')

    def trend_by_course(self):
        return self.df.groupby(['term_code', 'course'])['session_duration'].mean().reset_index()

    def returning_vs_new_users(self):
        self.df = self.df.sort_values(['userid', 'session_start'])
        self.df['first_session_week'] = self.df.groupby('userid')['study_week'].transform('min')
        self.df['user_type'] = np.where(self.df['study_week'] == self.df['first_session_week'], 'New', 'Returning')
        user_type_week = self.df.groupby(['study_week', 'user_type'])['userid'].nunique().reset_index(name='user_count')
        return user_type_week

    def session_time_of_day_buckets(self):
        self.df['hour'] = self.df['session_start'].dt.hour
        self.df['time_bucket'] = self.df['hour'].apply(time_bucket)
        return self.df['time_bucket'].value_counts().reset_index(name='count').rename(columns={'index': 'time_bucket'})

    def session_gaps(self):
        self.df = self.df.sort_values(['userid', 'session_start'])
        self.df['prev_end'] = self.df.groupby('userid')['session_end'].shift(1)
        self.df['gap_minutes'] = (self.df['session_start'] - self.df['prev_end']).dt.total_seconds() / 60
        return self.df[['userid', 'session_start', 'gap_minutes']].dropna()

    def compute_user_trends(self):
        self.df['term_num'] = self.df['term_code'].str.extract(r'(\d+)$').astype(int)
        trend_results = []

        for user, group in self.df.groupby('userid'):
            if len(group) < 2:
                continue
            X = group['term_num'].values.reshape(-1, 1)
            y = group['session_duration'].values
            model = LinearRegression().fit(X, y)
            slope = model.coef_[0]
            trend_results.append({'userid': user, 'trend_slope': slope, 'n_terms': len(group)})

        return pd.DataFrame(trend_results)

    def compute_course_trend(self):
        self.df['term_num'] = self.df['term_code'].str.extract(r'(\d+)$').astype(int)
        course_group = self.df.groupby('term_num')['session_duration'].mean().reset_index()

        if len(course_group) < 2:
            return None

        X = course_group['term_num'].values.reshape(-1, 1)
        y = course_group['session_duration'].values
        model = LinearRegression().fit(X, y)
        return model.coef_[0]

    def forum_activity_by_time_of_day(self, forum_df):
        df = forum_df.copy()
        df['event_time'] = pd.to_datetime(df['event_time'])
        df['hour'] = df['event_time'].dt.hour
        df['time_bucket'] = df['hour'].apply(time_bucket)
        df['study_week'] = df['event_time'].dt.isocalendar().week
        df = df[df['study_week'].between(1, 10)]
        df['forum_event_count'] = df.get('forum_event_count', 1)

        forum_by_week_time = df.groupby(['study_week', 'time_bucket'])['forum_event_count'].sum().unstack(fill_value=0)
        bucket_order = ['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night (Late)']
        forum_by_week_time = forum_by_week_time.reindex(columns=bucket_order, fill_value=0)

        return forum_by_week_time