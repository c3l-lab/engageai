
def lambda_handler(event, context):
    # Log event input (useful for debugging)
    print("Received event:", event)
    
    # Process the event (example: return a simple message)
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
