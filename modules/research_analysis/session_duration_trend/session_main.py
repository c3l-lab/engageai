import pandas as pd
import os
import sys

project_root = os.path.abspath(os.path.join(os.getcwd(), '../..'))
sys.path.append(project_root)

from session_utils import SessionProcessor
from trend_analysis import TrendAnalyzer
from session_visualisation import Visualizer
from module.data_pipeline.data_aws_import_singledf import read_single_csv_from_s3

def run_s3_pipeline():
    arn = "arn:aws:s3:::engage-ai-dataset"
    file_keys = ["term2405_course3547_alllog.csv"] 

    processor = SessionProcessor(course_filter=None)  # temporarily disabled course filtering
    session_frames = []

    for key in file_keys:
        df = read_single_csv_from_s3(arn, key)
        term_code = key.split('_')[0]
        processed = processor.process_dataframe(df, term_code=term_code)
        session_frames.append(processed)

    session_df = pd.concat(session_frames, ignore_index=True)
    print("Session DataFrame shape:", session_df.shape)
    print(session_df.head())

    analyzer = TrendAnalyzer(session_df)

    # Trend metrics
    avg_weekly = analyzer.avg_session_duration_per_week()
    session_count = analyzer.session_count_per_week()
    active_users = analyzer.active_users_per_week()
    dist = analyzer.session_duration_distribution(bins=[0, 5, 15, 30, 60, 120, 240])
    course_trend = analyzer.trend_by_course()
    user_types = analyzer.returning_vs_new_users()
    tod = analyzer.session_time_of_day_buckets()
    gaps = analyzer.session_gaps()

    # User and course trend slopes
    avg_term_df = processor.aggregate_avg_session_duration(session_df)
    analyzer_terms = TrendAnalyzer(avg_term_df, pre_aggregated=True)
    trend_df = analyzer_terms.compute_user_trends()
    course_slope = analyzer_terms.compute_course_trend()

    # Visuals
    Visualizer.plot_avg_session_duration_per_week(avg_weekly)
    Visualizer.plot_session_count_per_week(session_count)
    Visualizer.plot_active_users_per_week(active_users)
    Visualizer.plot_session_duration_distribution(dist)
    Visualizer.plot_returning_vs_new_users(user_types)
    Visualizer.plot_session_time_of_day(tod)
    Visualizer.plot_session_gaps(gaps)

    print("Course-wide trend slope:", course_slope)
    print("Pipeline complete. Plots saved to output folder.")

if __name__ == "__main__":
    run_s3_pipeline()
