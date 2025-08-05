from athena_query.assign_duedate_query import data_transformation

def lambda_handler(event, context):
    ret = data_transformation()
    # Log event input (useful for debugging)
    print("Received event:", event)
    print(ret)
    
    # Process the event (example: return a simple message)
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }



def lambda_handler(event, context):
    # Your code here
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


import boto3
import time

ATHENA_DATABASE = 'my_database'
ATHENA_TABLE = 'raw_data_table'
OUTPUT_S3 = 's3://processed-data-bucket/athena-results/'

def lambda_handler(event, context):
    # 1. Athena client
    client = boto3.client('athena')

    # 2. Start query
    query = f"""
        SELECT column1, COUNT(*) as count
        FROM {ATHENA_TABLE}
        GROUP BY column1
    """

    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        ResultConfiguration={'OutputLocation': OUTPUT_S3}
    )

    # 3. Wait for query to complete
    query_id = response['QueryExecutionId']
    while True:
        result = client.get_query_execution(QueryExecutionId=query_id)
        state = result['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(2)

    if state != 'SUCCEEDED':
        raise Exception("Athena query failed!")

    # 4. Download and analyze result
    s3 = boto3.client('s3')
    result_key = f'athena-results/{query_id}.csv'
    s3.download_file('processed-data-bucket', result_key, '/tmp/result.csv')

    # 5. Do analysis (simple example)
    import pandas as pd
    df = pd.read_csv('/tmp/result.csv')
    print("Basic summary:\n", df.describe())
    
    # (Optional: Save result or trigger another service)
