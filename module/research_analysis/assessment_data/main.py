import sys
import os

# Get current script's dir
current_dir = os.path.dirname(__file__)
research_analysis_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(research_analysis_dir)

from common_function import read_single_csv_from_s3

arn = "arn:aws:s3:::engage-ai-dataset"
file_key_log = "term2405_course3547_alllog.csv"
file_key_finalgrade = "allterm_course163601_finalgrade.csv"

df_log = read_single_csv_from_s3(arn, file_key_log)
df_finalgrade = read_single_csv_from_s3(arn, file_key_finalgrade )

print(df_log.head())
print(df_finalgrade.head())