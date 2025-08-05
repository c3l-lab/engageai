import boto3
import pandas as pd
import io
from dotenv import load_dotenv
import os

def cmid_section_df():

    load_dotenv()

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # Optional

    # Initialize a session with AWS
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )

    s3 = session.client("s3", region_name="ap-southeast-2")

    # Define bucket and object key
    bucket_name = "engage-ai-dataset"
    key = "map_assign_cmid_section/map_assign_cmid_instance.csv"

    # Fetch and read CSV into DataFrame
    response = s3.get_object(Bucket=bucket_name, Key=key)
    df = pd.read_csv(io.BytesIO(response['Body'].read()))

    return df

def filter_term_cmid(df,course: int):
    df = df[df['course'] == course]
    return df



# assign_cmid_section_df=cmid_section_df()
# print(assign_cmid_section_df.columns)
# print(assign_cmid_section_df)
# filter_assign_cmid_section_df=filter_term_cmid(assign_cmid_section_df, course=4177)
# print(filter_assign_cmid_section_df)