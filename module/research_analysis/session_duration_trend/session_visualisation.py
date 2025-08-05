import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

# Resolve output path relative to this file
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

class Visualizer:

    @staticmethod
    def _filter_weeks(df):
        return df[df['study_week'].between(1, 10)] if 'study_week' in df.columns else df

    @staticmethod
    def plot_avg_session_duration_per_week(df):
        df = Visualizer._filter_weeks(df)
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='study_week', y='session_duration', marker='o')
        plt.title("Average Session Duration per Week")
        plt.xlabel("Study Week")
        plt.ylabel("Avg Duration (min)")
        plt.grid(True)
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/avg_session_duration_per_week.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_session_count_per_week(df):
        df = Visualizer._filter_weeks(df)
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x='study_week', y='num_sessions', color='steelblue')
        plt.title("Session Count per Week")
        plt.xlabel("Study Week")
        plt.ylabel("Number of Sessions")
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/session_count_per_week.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_active_users_per_week(df):
        df = Visualizer._filter_weeks(df)
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='study_week', y='active_users', marker='o', color='green')
        plt.title("Active Users per Week")
        plt.xlabel("Study Week")
        plt.ylabel("Unique Users")
        plt.grid(True)
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/active_users_per_week.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_session_duration_distribution(df):
        total = df['count'].sum()
        df['percent'] = (df['count'] / total * 100).round(1)
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(data=df, x='duration_bin', y='count', palette='viridis')
        for i, row in df.iterrows():
            ax.text(i, row['count'] + 100, f"{row['percent']}%", ha='center')
        plt.title("Session Duration Distribution")
        plt.xlabel("Session Duration Range (min)")
        plt.ylabel("Number of Sessions")
        plt.xticks(rotation=45)
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/session_duration_distribution.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_course_trend(df):
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x='term_code', y='session_duration', hue='course', marker='o')
        plt.title("Session Duration Trend by Course")
        plt.xlabel("Term")
        plt.ylabel("Avg Duration (min)")
        plt.grid(True)
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/course_trend.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_returning_vs_new_users(df):
        df = Visualizer._filter_weeks(df)
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x='study_week', y='user_count', hue='user_type', palette='Set2')
        plt.title("New vs Returning Users per Week")
        plt.xlabel("Study Week")
        plt.ylabel("User Count")
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/returning_vs_new_users.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_session_time_of_day(df):
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x='time_bucket', y='count', palette='coolwarm')
        plt.title("Session Distribution by Time of Day")
        plt.xlabel("Time of Day")
        plt.ylabel("Number of Sessions")
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/session_time_of_day.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_session_gaps(df):
        # Bin gaps into meaningful intervals
        bins = [0, 60, 360, 1440, 10080, float('inf')]  # 1h, 6h, 1d, 7d, >7d
        labels = ['<1h', '1–6h', '6–24h', '1–7d', '>7d']
        df['gap_category'] = pd.cut(df['gap_minutes'], bins=bins, labels=labels, right=False)
        gap_dist = df['gap_category'].value_counts().sort_index().reset_index()
        gap_dist.columns = ['gap_category', 'count']
        plt.figure(figsize=(10, 6))
        sns.barplot(data=gap_dist, x='gap_category', y='count', palette='Purples')
        plt.title("Distribution of Session Gaps by Category")
        plt.xlabel("Gap Between Sessions")
        plt.ylabel("Frequency")
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/session_gaps.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()

    @staticmethod
    def plot_forum_time_buckets(forum_by_week_time):
        forum_by_week_time = forum_by_week_time.loc[forum_by_week_time.index.isin(range(1, 11))]
        forum_by_week_time.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='tab20')
        plt.title('Forum Activities by Time of Day and Week')
        plt.xlabel('Study Week')
        plt.ylabel('Total Forum Event Count')
        plt.legend(title='Time of Day', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/forum_time_buckets.png"
        print("Saving to:", path)
        plt.savefig(path)
        plt.close()