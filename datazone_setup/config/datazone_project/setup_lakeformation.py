import boto3

profile_name= 'c3l-analytics'
region_name='ap-southeast-2'
SESSION = boto3.Session(profile_name='c3l-analytics')  # Replace with your actual profile
lakeformation = SESSION.client('lakeformation', region_name='ap-southeast-2')



s3_path = 's3://engage-ai-dataset/engageai_indicator/'


def lakeformation_grant():
    response = lakeformation.grant_permissions(
        Principal={
            'DataLakePrincipalIdentifier': 'arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution'  # e.g., DataZone Execution Role
        },
        Resource={
            'DataLocation': {
                'ResourceArn': 'arn:aws:s3:::engage-ai-dataset/engageai_indicator'
            }
        },
        Permissions=['DATA_LOCATION_ACCESS']
    )

    print("[✔] Granted Lake Formation permission to S3 location")

lakeformation_grant()