import os
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

curr_dir = os.path.abspath(__file__)
sys.path.append( os.path.abspath(os.path.join(curr_dir, "../../../../")))
sys.path.append(os.path.abspath(os.path.join(curr_dir, "../../..")))

from lambdas.athena_query.data_process import full_assignment_submission_pipeline
from lambdas.athena_query.AthenaQueryRunner import AthenaQueryRunner


load_dotenv()

credentials = {
    'AWS_ACCESS_KEY_ID': os.getenv("AWS_ACCESS_KEY_ID"),
    'AWS_SECRET_ACCESS_KEY': os.getenv("AWS_SECRET_ACCESS_KEY"),
    'AWS_SESSION_TOKEN': os.getenv("AWS_SESSION_TOKEN")
}

### can alter course_id = 4177
course_id = 4177

def main():
        
        print(f"📚 Running pipeline for course_id={course_id}...")
        pipeline_df = full_assignment_submission_pipeline(course_id=course_id)

        # Step 5: Upload to S3
        runner = AthenaQueryRunner(credentials)
        timestamp_str = datetime.today().strftime('%Y%m%d_%H%M%S')  # e.g., 20250806_113045
        s3_key = f'engageai_indicator/{timestamp_str}_SubmissionScoreIndicator.csv'
        runner.upload_dataframe_to_s3(pipeline_df, s3_key)
        print("✅ Pipeline execution and upload completed.")


def lambda_handler(event, context):
    try:
        main()
        return {
            'statusCode': 200,
            'body': 'Lambda executed successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }