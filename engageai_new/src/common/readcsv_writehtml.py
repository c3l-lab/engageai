import os
import boto3
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

def read_csv_s3(bucket: str, key: str) -> pd.DataFrame:
    """Read CSV file from S3 and return as DataFrame."""
    load_dotenv()

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # optional

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )

    s3_client = session.client("s3", region_name="ap-southeast-2")
    csv_obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = csv_obj["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(body))
    return df


def add_section(html_sections: list, title: str, content: str, start=None, end=None, include_dates=False):
    """Append a section to html_sections with optional start/end dates."""
    if include_dates and start and end:
        title = f"{title} ({start} to {end})"
    html_sections.append(f"<h2>{title}</h2>\n{content}<hr>")


def write_html(html_sections: list, start: str, end: str) -> str:
    """Generate HTML template from sections and return as string."""
    html_template = f"""
    <html>
    <head>
        <title>Weekly Submission Report {start} - {end}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #2c3e50; margin-top: 40px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f4f4f4; }}
            hr {{ margin: 40px 0; }}
        </style>
    </head>
    <body>
        <h1>Weekly Submission/Assessment Data Report: {start} to {end}</h1>
        {"".join(html_sections)}
    </body>
    </html>
    """
    return html_template


def save_html_s3(html_content: str, start: str, end: str, bucket: str = "engage-ai-dataset", prefix: str = "output_html/"):
    """Upload HTML content directly to S3."""
    load_dotenv()
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # optional

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )

    s3_client = session.client("s3", region_name="ap-southeast-2")

    file_name = f"weekly_report_{start.replace('/','')}_{end.replace('/','')}.html"
    s3_key = f"{prefix}{file_name}"

    s3_client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=html_content,
        ContentType="text/html"
    )

    print(f"✅ HTML report uploaded to s3://{bucket}/{s3_key}")





# import os
# from io import StringIO
# import boto3
# import pandas as pd
# from dotenv import load_dotenv
# from engageai_new.test.test_assessment_t import html_sections

# def read_csv_s3(bucket: str, key: str) -> pd.DataFrame:

#     load_dotenv()  # Load AWS credentials from .env

#     aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
#     aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
#     aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # optional

#     # Initialize boto3 session
#     session = boto3.Session(
#         aws_access_key_id=aws_access_key_id,
#         aws_secret_access_key=aws_secret_access_key,
#         aws_session_token=aws_session_token
#     )

#     s3_client = session.client("s3", region_name="ap-southeast-2")

#     # Get object from S3
#     csv_obj = s3_client.get_object(Bucket=bucket, Key=key)
#     body = csv_obj["Body"].read().decode("utf-8")
#     df = pd.read_csv(StringIO(body))

#     return df

# def add_section(title, content, include_dates=False, start=None, end=None):
#     if start is None:
#         start = globals().get("start", "")
#     if end is None:
#         end = globals().get("end", "")

#     if include_dates:
#         title = f"{title} ({start} to {end})"
#     html_sections.append(f"<h2>{title}</h2>\n{content}<hr>")


# def write_html(html_sections, start: str, end: str) -> str:
#     """
#     Generate the full HTML content from html_sections and return it as a string.
#     Does NOT save locally.
#     """
#     html_template = f"""
#     <html>
#     <head>
#         <title>Weekly Submission Report {start} - {end}</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 20px; }}
#             h1 {{ color: #2c3e50; }}
#             h2 {{ color: #2c3e50; margin-top: 40px; }}
#             table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
#             th, td {{ border: 1px solid #ddd; padding: 8px; }}
#             th {{ background-color: #f4f4f4; }}
#             hr {{ margin: 40px 0; }}
#         </style>
#     </head>
#     <body>
#         <h1>Weekly Submission/ Assessment Data Report: {start} to {end}</h1>
#         {"".join(html_sections)}
#     </body>
#     </html>
#     """
#     return html_template


# ####### write_html function that saves locally (not used) #######
# # def write_html(html_sections, start: str, end: str, output_dir: str = ".") -> str:
# #     html_template = f"""
# #     <html>
# #     <head>
# #         <title>Weekly Submission Report {start} - {end}</title>
# #         <style>
# #             body {{ font-family: Arial, sans-serif; margin: 20px; }}
# #             h1 {{ color: #2c3e50; }}
# #             h2 {{ color: #2c3e50; margin-top: 40px; }}
# #             table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
# #             th, td {{ border: 1px solid #ddd; padding: 8px; }}
# #             th {{ background-color: #f4f4f4; }}
# #             hr {{ margin: 40px 0; }}
# #         </style>
# #     </head>
# #     <body>
# #         <h1>Weekly Submission/ Assessment Data Report: {start} to {end}</h1>
# #         {"".join(html_sections)}
# #     </body>
# #     </html>
# #     """

# #     os.makedirs(output_dir, exist_ok=True)

# #     output_file = os.path.join(
# #         output_dir, f"weekly_report_{start.replace('/','')}_{end.replace('/','')}.html"
# #     )

# #     with open(output_file, "w", encoding="utf-8") as f:
# #         f.write(html_template)

# #     print(f"✅ HTML report generated: {output_file}")
# #     return output_file



# # Save HTML to S3 (fixed bucket & folder)
# def save_html_s3(html_content: str, start: str, end: str):
#     load_dotenv()
#     session = boto3.Session(
#         aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#         aws_session_token=os.getenv("AWS_SESSION_TOKEN")  # optional
#     )
#     s3_client = session.client("s3", region_name="ap-southeast-2")

#     bucket = "engage-ai-dataset"          # fixed bucket
#     output_dir = "output_html"            # fixed folder
#     filename = f"weekly_report_{start.replace('/', '')}_{end.replace('/', '')}.html"
#     key = f"{output_dir}/{filename}"

#     s3_client.put_object(
#         Bucket=bucket,
#         Key=key,
#         Body=html_content,
#         ContentType="text/html"
#     )
#     print(f"✅ HTML uploaded to s3://{bucket}/{key}")

# # def save_html_s3(html_content: str, bucket: str, key: str):

# #     load_dotenv()  # Load AWS credentials from .env

# #     aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
# #     aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
# #     aws_session_token = os.getenv("AWS_SESSION_TOKEN")  # optional

# #     # Initialize boto3 session
# #     session = boto3.Session(
# #         aws_access_key_id=aws_access_key_id,
# #         aws_secret_access_key=aws_secret_access_key,
# #         aws_session_token=aws_session_token
# #     )

# #     s3_client = session.client("s3", region_name="ap-southeast-2")

# #     # Upload the HTML content
# #     s3_client.put_object(
# #         Bucket=bucket,
# #         Key=key,
# #         Body=html_content,
# #         ContentType="text/html"
# #     )

# #     print(f"✅ HTML uploaded to s3://{bucket}/{key}")
