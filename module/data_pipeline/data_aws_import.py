import boto3
import pandas as pd
from io import StringIO

#### Read ALL FILES 
# Loaded: term2405_course3547_alllog.csv
# Loaded: term2412_course3653_alllog.csv
# Loaded: term2414_course3847_alllog.csv
# Loaded: term2425_course4177_alllog.csv


def list_and_read_csv_from_arn(arn_location, profile_name='c3l-analytics'):
 
    # Extract bucket name
    if not arn_location.startswith("arn:aws:s3:::"):
        raise ValueError("Invalid S3 ARN format")
    
    bucket_name = arn_location.replace("arn:aws:s3:::", "")

    # Initialize boto3 session and client
    session = boto3.Session(profile_name=profile_name)
    s3_client = session.client("s3")
    
    # List all objects
    all_keys = []
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name)

    for page in pages:
        contents = page.get("Contents", [])
        for obj in contents:
            key = obj["Key"]
            if key.endswith(".csv"):
                all_keys.append(key)

    # Read each CSV file into a DataFrame and store in a dictionary
    dataframes = {}
    for key in all_keys:
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        body = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(body))
        filename = key.split('/')[-1]
        dataframes[filename] = df
        print(f"Loaded: {filename}")

    return dataframes

# Example usage
if __name__ == "__main__":
    arn = "arn:aws:s3:::engage-ai-dataset"
    csv_data = list_and_read_csv_from_arn(arn)

    # Preview one file
    for name, df in csv_data.items():
        print(f"\n{name} preview:\n", df.head())
