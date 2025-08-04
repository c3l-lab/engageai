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
