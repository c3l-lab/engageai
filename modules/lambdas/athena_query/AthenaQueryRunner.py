import boto3
import time
import os
from dotenv import load_dotenv

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
