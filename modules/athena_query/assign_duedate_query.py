# import boto3
# import os
# import time
# from dotenv import load_dotenv

# load_dotenv()

# AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_SESSION_TOKEN=os.getenv("AWS_SESSION_TOKEN")


# # Athena configuration
# region = 'ap-southeast-2'
# database = 'engage-ai-dataset'  # Replace with actual DB name
# query = '''
# SELECT 
# DISTINCT term_code, 
# moodle_course_id, 
# id,
# iteminstance,
# duedate,
# name
# FROM "engage-ai-dataset"."every_termcode_assign_module_duedate"

# '''  # Replace with your query

# output_location = 's3://engage-ai-dataset/athena-result/csv_to_needcol/'

# # Initialize Athena client with credentials
# athena = boto3.client(
#     'athena',
#     region_name=region,
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     aws_session_token=AWS_SESSION_TOKEN  # This line is important for temporary credentials
# )

# # Start query execution
# response = athena.start_query_execution(
#     QueryString=query,
#     QueryExecutionContext={'Database': database},
#     ResultConfiguration={'OutputLocation': output_location}
# )

# # Get query execution ID
# query_execution_id = response['QueryExecutionId']
# print(f"Started Athena query. Execution ID: {query_execution_id}")

# # Wait for completion
# while True:
#     result = athena.get_query_execution(QueryExecutionId=query_execution_id)
#     state = result['QueryExecution']['Status']['State']

#     if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
#         break
#     print(f"Query status: {state}... waiting.")
#     time.sleep(2)

# # Final result
# if state == 'SUCCEEDED':
#     result_path = result['QueryExecution']['ResultConfiguration']['OutputLocation']
#     print(f"✅ Query succeeded. Result saved to:\n{result_path}")
# else:
#     print(f"❌ Query failed or cancelled. Status: {state}")


#########

import os
import sys

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
runner = AthenaQueryRunner(credentials)


def data_transformation(**kwargs):
    # Step 3: Define your query, database, and S3 output
    database = 'engage-ai-dataset'
    sql_query = '''
    SELECT DISTINCT term_code, moodle_course_id, id, iteminstance, duedate, name
    FROM "engage-ai-dataset"."every_termcode_assign_module_duedate"
    LIMIT 100
    '''
    s3_output = 's3://engage-ai-dataset/athena-result/csv_to_needcol/format_csv_assign_duedate/'
    
    
    
    # Step 4: Run the query
    result_url = runner.run_query(database, sql_query, s3_output)
    return result_url
