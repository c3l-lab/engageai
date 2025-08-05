import os
import sys
import pandas as pd
import boto3
import io

cur_dir=os.path.abspath(__file__)
sys.path.append(cur_dir)

from AthenaQueryRunner import *
from dotenv import load_dotenv
load_dotenv()

# Step 1: Load AWS credentials from .env
credentials = {
    'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
    'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
    'AWS_SESSION_TOKEN': os.getenv("AWS_SESSION_TOKEN")
}

# Step 2: Create AthenaQueryRunner instance
# runner = AthenaQueryRunner(credentials)


# def data_transformation(**kwargs):
#     # Step 3: Define your query, database, and S3 output
#     database = 'engage-ai-dataset'
#     sql_query = '''
#     SELECT DISTINCT term_code, moodle_course_id, id, iteminstance, duedate, name
#     FROM "engage-ai-dataset"."every_termcode_assign_module_duedate"
#     LIMIT 100
#     '''
#     s3_output = 's3://engage-ai-dataset/athena-result/csv_to_needcol/format_csv_assign_duedate/'
    
    
    
#     # Step 4: Run the query
#     result_url = runner.run_query(database, sql_query, s3_output)
#     return result_url


def data_transformation(**kwargs):
    # Step 1: Set query details
    database = 'engage-ai-dataset'
    sql_query = '''
    SELECT DISTINCT term_code, moodle_course_id, id, iteminstance, duedate, name
    FROM "engage-ai-dataset"."every_termcode_assign_module_duedate"
    LIMIT 100
    '''
    s3_output = 's3://engage-ai-dataset/athena-result/csv_to_needcol/format_csv_assign_duedate/'

    runner = AthenaQueryRunner(credentials)
    # Step 2: Run Athena query
    result_s3_path = runner.run_query(database, sql_query, s3_output)

    # Step 3: Extract bucket and key
    if result_s3_path.startswith("s3://"):
        s3_path_parts = result_s3_path.replace("s3://", "").split("/", 1)
        bucket_name = s3_path_parts[0]
        object_key = s3_path_parts[1]

        # Step 4: Read S3 object into DataFrame
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        
        return df
    else:
        raise ValueError("Invalid S3 path returned by runner.run_query")


# assign_duedate_df=data_transformation()
# print(assign_duedate_df)