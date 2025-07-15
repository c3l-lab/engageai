import boto3
import pandas as pd
from io import StringIO

def read_single_csv_from_s3(arn_location, file_key, profile_name='c3l-analytics'):

    if not arn_location.startswith("arn:aws:s3:::"):
        raise ValueError("Invalid S3 ARN format")
    
    bucket_name = arn_location.replace("arn:aws:s3:::", "")
    session = boto3.Session(profile_name=profile_name)
    s3_client = session.client("s3")

    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    body = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(body))

    print(f"Loaded CSV: {file_key} — Shape: {df.shape}")
    return df

# Example usage
if __name__ == "__main__":
    arn = "arn:aws:s3:::engage-ai-dataset"
    file_key = "term2405_course3547_alllog.csv"  # Full key/path within the bucket

    df_alllog = read_single_csv_from_s3(arn, file_key)

    # Preview data
    print(df_alllog.head())


# import boto3
# import pandas as pd
# from io import StringIO

# def read_single_csv_from_s3(arn_location, file_key, profile_name='c3l-analytics'):
#     """
#     Reads a single CSV file from an S3 bucket specified by ARN.
#     """
#     if not arn_location.startswith("arn:aws:s3:::"):
#         raise ValueError("Invalid S3 ARN format")
    
#     bucket_name = arn_location.replace("arn:aws:s3:::", "")
#     session = boto3.Session(profile_name=profile_name)
#     s3_client = session.client("s3")

#     obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
#     body = obj['Body'].read().decode('utf-8')
#     df = pd.read_csv(StringIO(body))

#     return df
