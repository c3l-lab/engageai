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

# Step 3: Define your query, database, and S3 output
database = 'engage-ai-dataset'
sql_query = '''
SELECT DISTINCT * FROM "engage-ai-dataset"."term_course_alllog"
WHERE action ='submit for grading'
AND course= 3547
'''
s3_output = 's3://engage-ai-dataset/athena-result/csv_to_needcol/format_csv_student_sub/'

# Step 4: Run the query
result_url = runner.run_query(database, sql_query, s3_output)
