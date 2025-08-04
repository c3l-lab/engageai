import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'access_frequency', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def plot_weekly_totals(weekly_totals):
    plt.figure(figsize=(10, 5))
    sns.barplot(data=weekly_totals, x='study_week', y='active_days', palette='Blues_d')
    plt.title('Total Active Days per Study Week (Weeks 1–10)')
    plt.xlabel('Study Week')
    plt.ylabel('Total Active Days')
    save_plot('weekly_totals.png')

def plot_active_users(user_counts):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=user_counts, x='study_week', y='active_users', palette='Greens_d', ax=ax1)
    ax1.set_ylabel('Active Users', color='green')
    ax2 = ax1.twinx()
    sns.lineplot(data=user_counts, x='study_week', y='pct_change', color='black', marker='o', ax=ax2)
    ax2.set_ylabel('% Change from Previous Week', color='black')
    ax2.axhline(0, color='gray', linestyle='--')
    plt.title('Active Users and % Change (Weeks 1–10)')
    save_plot('active_users_pct_change.png')

def plot_slope_distribution(user_slopes_df):
    plt.figure(figsize=(8, 4))
    sns.histplot(user_slopes_df['slope'], bins=30, kde=True)
    plt.title('Distribution of User Engagement Slopes')
    plt.xlabel('Slope of Weekly Activity')
    plt.ylabel('Number of Users')
    plt.axvline(0, color='red', linestyle='--', label='No Change')
    plt.legend()
    save_plot('slope_distribution.png')

def plot_at_risk_split(risk_summary):
    plt.figure(figsize=(7, 5))
    ax = sns.barplot(data=risk_summary, x='Risk_Category', y='User_Count', palette='Set1')
    for i, row in risk_summary.iterrows():
        ax.text(i, row['User_Count'] + 1, f"{row['Percentage']}%", ha='center', va='bottom', fontsize=12, fontweight='bold')
    plt.title('Users At Risk of Disengagement (≥30% Drop in Activity)')
    plt.xlabel('User Category')
    plt.ylabel('User Count')
    save_plot('at_risk_users.png')