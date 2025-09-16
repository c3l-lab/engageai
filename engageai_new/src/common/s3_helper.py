import boto3
import pandas as pd
import json
from io import BytesIO

# Use default session with your SSO profile
session = boto3.Session(profile_name="c3l-analytics") 
s3_client = session.client("s3")


def read_csv_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Read CSV from S3 directly into a pandas DataFrame without downloading locally.
    """
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(BytesIO(obj['Body'].read()))


def read_json_s3(bucket: str, key: str) -> dict:
    """
    Read JSON from S3 directly into a Python dictionary.
    """
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return json.loads(obj['Body'].read().decode('utf-8'))


def list_s3_objects(bucket: str, prefix: str = "") -> list:
    """
    List objects in S3 bucket (optionally filtered by prefix).
    """
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [item['Key'] for item in response.get('Contents', [])]


