import boto3
import pandas as pd
from io import StringIO
import traceback
from data_pipeline.logger import get_logger

logger = get_logger(__name__)
def read_single_csv_from_s3(file_key, bucket_name="engage-ai-dataset", profile_name='c3l-analytics'):
    df = None
    try:
        session = boto3.Session(profile_name=profile_name)
        s3_client = session.client("s3")

        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        body = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(body))

        print(f"Loaded CSV: {file_key} — Shape: {df.shape}")
    except Exception as e:
        logger.error(f"File Key:{file_key}   bucket_name: {bucket_name}")
        traceback.print_exc()
    return df

# Example usage
if __name__ == "__main__":
    bucket_name= 'engage-ai-dataset'
    object_key= 'term2405_course3547_alllog.csv'

    df_alllog = read_single_csv_from_s3(object_key,bucket_name)
    # Preview data
    print(df_alllog.head())

