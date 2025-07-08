import sys
import os

# Get current script's dir
current_dir = os.path.dirname(__file__)
research_analysis_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(research_analysis_dir)

from common_function import read_single_csv_from_s3

arn = "arn:aws:s3:::engage-ai-dataset"
file_key = "term2405_course3547_alllog.csv"

df = read_single_csv_from_s3(arn, file_key)

print(df.head())
