import boto3
import time
import os
import json
from botocore.exceptions import ClientError

profile_name= 'c3l-analytics'
region_name='ap-southeast-2'
SESSION = boto3.Session(profile_name='c3l-analytics')  # Replace with your actual profile
datazone = SESSION.client('datazone', region_name='ap-southeast-2')
athena = SESSION.client('athena', region_name=region_name)

import boto3

def add_member_to_project(domain_id, project_id, member_type, member_identifier, role='CONTRIBUTOR'):
    response = datazone.create_project_membership(
        domainIdentifier=domain_id,
        projectIdentifier=project_id,
        designation='CONTRIBUTOR',  # project role
        member={
            "type": "ROLE",  # or USER or GROUP
            "principal": {
                "arn": "arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520"
            }
        }
    )
    print("Membership added:", response)


# # Example usage:
# domain_id = 'your-domain-id'
# project_id = 'your-project-id'
member_type = 'ROLE'  # or 'GROUP' or 'ROLE'
member_identifier = 'arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520'  # example IAM user ARN
role = 'CONTRIBUTOR'

# add_member_to_project(domain_id, project_id, member_type, member_identifier, role)


def list_environment_blueprint_configurations(domain_id):
    response = datazone.list_environment_blueprint_configurations(
        domainIdentifier=domain_id,
        maxResults=50
    )
    configs = response.get('items', [])
    blueprint_ids = []
    for config in configs:
        blueprint_id = config.get('environmentBlueprintId')
        print(f"Blueprint ID: {blueprint_id}, Regions: {config.get('enabledRegions')}")
        if blueprint_id:
            blueprint_ids.append(blueprint_id)
    return blueprint_ids

def create_environment_profile(domain_id, project_id, blueprint_id, profile_name="EnvProfile", description="Environment Profile"):
    response = datazone.create_environment_profile(
        domainIdentifier=domain_id,
        name=profile_name,
        description=description,
        projectId=project_id,
        blueprintId=blueprint_id
    )
    env_profile_id = response['id']
    print(f"Created environment profile with ID: {env_profile_id}")
    return env_profile_id

def create_environment(domain_id, project_id, env_profile_id, environment_name="EnvName", description="Environment description"):
    response = datazone.create_environment(
        domainIdentifier=domain_id,
        projectId=project_id,
        environmentProfileId=env_profile_id,
        name=environment_name,
        description=description
    )
    env_id = response['id']
    print(f"Created environment with ID: {env_id}")
    return env_id

def create_glue_data_source(domain_id, project_id, env_id, data_source_name, glue_db_name, glue_role_arn):
    glue_config = {
        "glueRunConfiguration": {
            "catalogName": "AwsDataCatalog",
            "dataAccessRole": glue_role_arn,
            "relationalFilterConfigurations": [
                {
                    "databaseName": glue_db_name,
                    "filterExpressions": [{"expression": "*", "type": "INCLUDE"}]
                }
            ]
        }
    }

    response = datazone.create_data_source(
        domainIdentifier=domain_id,
        projectId=project_id,
        name=data_source_name,
        type='GLUE',
        configuration=glue_config,
        environmentId=env_id,
        publishOnImport=True
    )
    data_source_id = response['id']
    print(f"Created Glue data source with ID: {data_source_id}")
    return data_source_id

def run_athena_query(query, database, output_location):
    """Run an Athena query and return the query execution ID."""
    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        query_execution_id = response['QueryExecutionId']
        print(f"Athena query started with execution ID: {query_execution_id}")
        return query_execution_id
    except ClientError as e:
        print(f"Athena query failed: {e}")
        return None

def wait_for_athena_query(query_execution_id):
    """Wait for Athena query to complete and return the status."""
    import time
    while True:
        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            print(f"Athena query status: {status}")
            return status
        print("Waiting for Athena query to complete...")
        time.sleep(5)

def get_athena_query_results(query_execution_id):
    """Fetch Athena query results."""
    response = athena.get_query_results(QueryExecutionId=query_execution_id)
    results = response['ResultSet']['Rows']
    for row in results:
        print([col.get('VarCharValue') for col in row['Data']])

# # === Example Usage ===
# def main():
# domain_id = 'your-domain-id'
# project_id = 'your-project-id'
# glue_db_name = 'your_glue_database_name'
# glue_role_arn = 'arn:aws:iam::123456789012:role/your-glue-access-role'
# data_source_name = 'MyGlueDataSource'
# athena_output = 's3://your-athena-query-results-bucket/'

# Step 1: Get blueprint IDs

blueprint_ids = list_environment_blueprint_configurations(domain_id)
if not blueprint_ids:
print("No blueprint configurations found. Exiting.")
return

blueprint_id = blueprint_ids[0]  # Pick first blueprint

# Step 2: Create environment profile
env_profile_id = create_environment_profile(domain_id, project_id, blueprint_id)

# Step 3: Create environment
env_id = create_environment(domain_id, project_id, env_profile_id)

# Step 4: Create Glue data source
data_source_id = create_glue_data_source(domain_id, project_id, env_id, data_source_name, glue_db_name, glue_role_arn)

# Step 5 (Optional): Run Athena query
query = "SELECT * FROM your_table LIMIT 10;"
query_execution_id = run_athena_query(query, glue_db_name, athena_output)
if query_execution_id:
status = wait_for_athena_query(query_execution_id)
if status == 'SUCCEEDED':
get_athena_query_results(query_execution_id)

