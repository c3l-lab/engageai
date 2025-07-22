import pandas as pd

from research_analysis.access_frequency.access_freq_utils import (
    load_and_filter_access_data,
    compute_weekly_totals,
    compute_user_counts,
    compute_user_slope_matrix,
    categorize_slope,
    detect_30pct_drop_users
)

class AccessFrequencyAnalyzer:
    def __init__(self, df):
        self.df = load_and_filter_access_data(df)

    def analyze(self):
        weekly_totals = compute_weekly_totals(self.df)
        user_counts = compute_user_counts(self.df)
        return weekly_totals, user_counts

    def slope_analysis(self):
        slope_df = compute_user_slope_matrix(self.df)
        slope_df['trend_category'] = slope_df['slope'].apply(categorize_slope)
        return slope_df

    def dropoff_analysis(self):
        drop_df = detect_30pct_drop_users(self.df)
        total_users = self.df['userid'].nunique()
        at_risk_users = len(drop_df)
        not_at_risk = total_users - at_risk_users
        summary = {
            'Risk_Category': ['At Risk (≥30% drop)', 'Not At Risk'],
            'User_Count': [at_risk_users, not_at_risk]
        }
        risk_df = pd.DataFrame(summary)
        risk_df['Percentage'] = (risk_df['User_Count'] / total_users * 100).round(1)
        return risk_df
