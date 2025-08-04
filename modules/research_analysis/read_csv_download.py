
import os
import sys
import pandas as pd

def read_csv_from_module(base_dir, csv_name):

    # Construct the full path to the CSV file
    csv_path = os.path.join(base_dir, '..', 'download_data', csv_name)
    csv_path = os.path.abspath(csv_path)
    df= pd.read_csv(csv_path)

    # Read and return the DataFrame
    return  df.drop_duplicates()

# Example usage:
if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)

    df_finalgrade = read_csv_from_module(current_dir, 'allterm_course163601_finalgrade.csv')
    df_alllog = read_csv_from_module(current_dir, 'term2405_course3547_alllog.csv')  # fixed extension

    print(df_finalgrade.head())
    print(df_alllog.head())


### FETCHING FROM AWS 

# import sys
# import os

# # Get current script's dir
# current_dir = os.path.dirname(__file__)
# research_analysis_dir = os.path.abspath(os.path.join(current_dir, ".."))
# sys.path.append(research_analysis_dir)

# from common_function import read_single_csv_from_s3

# arn = "arn:aws:s3:::engage-ai-dataset"
# file_key_log = "term2405_course3547_alllog.csv"
# file_key_finalgrade = "allterm_course163601_finalgrade.csv"

# df_log = read_single_csv_from_s3(arn, file_key_log)
# df_finalgrade = read_single_csv_from_s3(arn, file_key_finalgrade )

# print(df_log.head())
# print(df_finalgrade.head())

######## FETCHING DATA FROM THE DOWNLOAD_DATA
