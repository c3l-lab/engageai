from research_analysis.access_frequency.analysis import AccessFrequencyAnalyzer
from research_analysis.access_frequency.access_frequency_visualisation import (
    plot_weekly_totals,
    plot_active_users,
    plot_slope_distribution,
    plot_at_risk_split
)
from data_pipeline.data_aws_import_singledf import read_single_csv_from_s3
from research_analysis.access_frequency.access_freq_utils import preprocess_access_frequency_from_logs


def main():
    arn = "arn:aws:s3:::engage-ai-dataset"
    file_key = "term2405_course3547_alllog.csv"
    term_start = "2024-01-08"


    df_logs = read_single_csv_from_s3(arn, file_key, profile_name='c3l-analytics')
    access_df = preprocess_access_frequency_from_logs(df_logs, term_start)

    analyzer = AccessFrequencyAnalyzer(access_df)
    weekly_totals, user_counts = analyzer.analyze()
    plot_weekly_totals(weekly_totals)
    plot_active_users(user_counts)

    slope_df = analyzer.slope_analysis()
    plot_slope_distribution(slope_df)

    risk_summary = analyzer.dropoff_analysis()
    plot_at_risk_split(risk_summary)


if __name__ == "__main__":
    main()
