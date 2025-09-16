import boto3
import time
import os
from dotenv import load_dotenv
import tempfile
import pandas as pd

class AthenaQueryRunner:
    def __init__(self, aws_credentials: dict, region: str = 'ap-southeast-2'):
        self.region = region
        self.aws_access_key_id = aws_credentials['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = aws_credentials['AWS_SECRET_ACCESS_KEY']
        self.aws_session_token = aws_credentials['AWS_SESSION_TOKEN']

        self.athena = boto3.client(
            'athena',
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token
        )
        
        self.s3 = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token
        )

    def run_query(self, database: str, query: str, output_path: str) -> str:
  
        response = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_path}
        )

        query_execution_id = response['QueryExecutionId']
        print(f"🔍 Query Execution ID: {query_execution_id}")

        # Polling until completion
        while True:
            result = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = result['QueryExecution']['Status']['State']

            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            print(f"Query status: {state}... waiting.")
            time.sleep(2)

        if state == 'SUCCEEDED':
            result_path = result['QueryExecution']['ResultConfiguration']['OutputLocation']
            print(f"✅ Query succeeded. Result saved to:\n{result_path}")
            return result_path
        else:
            print(f"❌ Query failed or cancelled. Status: {state}")
            return None
        
    def upload_to_s3(self, local_file_path: str, s3_key: str, bucket_name: str = 'engage-ai-dataset'):

        try:
            self.s3.upload_file(local_file_path, bucket_name, s3_key)
            print(f"✅ Uploaded '{local_file_path}' to s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"❌ Failed to upload to S3: {e}")
            raise

    
    def upload_dataframe_to_s3(self, df: pd.DataFrame, s3_key: str, bucket_name: str = 'engage-ai-dataset'):

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            temp_path = tmp_file.name
            df.to_csv(temp_path, index=False)
            print(f"📝 DataFrame saved to temporary file: {temp_path}")

        try:
            self.upload_to_s3(temp_path, s3_key, bucket_name)
        finally:
            os.remove(temp_path)
            print(f"🧹 Temp file deleted: {temp_path}")
