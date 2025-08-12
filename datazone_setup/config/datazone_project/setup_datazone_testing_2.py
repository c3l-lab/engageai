import boto3
import time
import os
import json
from botocore.exceptions import ClientError

profile_name= 'c3l-analytics'
region_name='ap-southeast-2'
SESSION = boto3.Session(profile_name='c3l-analytics')  # Replace with your actual profile
datazone = SESSION.client('datazone', region_name='ap-southeast-2')


def add_member_to_project(domain_id, project_id, member_type, member_identifier, role='CONTRIBUTOR'):
    response = datazone.create_project_membership(
        domainIdentifier=domain_id,
        projectIdentifier=project_id,
        designation='CONTRIBUTOR',  # project role
        member={
            "type": "groupIdentifier",  # or USER or GROUP
            "principal": {
                "arn": "arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520"
            }
        }
    )
    print("Membership added:", response)



# # Example usage:
# domain_id = 'your-domain-id'
# project_id = 'your-project-id'
# member_type = 'ROLE'  # or 'GROUP' or 'ROLE'
# member_identifier = 'arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520'  # example IAM user ARN
# role = 'CONTRIBUTOR'

# add_member_to_project(domain_id, project_id, member_type, member_identifier, role)



### ---------- Step 1: Create Domain ----------
def create_domain():
    # First, list existing domains and check if one with the target name exists
    response = datazone.list_domains()
    target_name = 'engage_ai_datazone'

    for domain in response.get('items', []):
        if domain.get('name') == target_name:
            domain_id = domain.get('id')
            print(f"[ℹ] Domain '{target_name}' already exists with ID: {domain_id}")
            return domain_id

    # If not found, create new domain
    response = datazone.create_domain(
        name=target_name,
        description='DataZone domain for Engage AI project',
        domainExecutionRole='arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution',
        kmsKeyIdentifier='arn:aws:kms:ap-southeast-2:184898280326:key/cfcbd85c-6eb3-47c4-b5e5-2dca0fce71c4'
    )
    domain_id = response['id']
    print(f"[✔] Domain created: {domain_id}")
    return domain_id


def get_datazone_domain_details(domain_identifier: str, profile_name: str = 'default', region: str = 'ap-southeast-2'):

    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        datazone = session.client('datazone')
        
        response = datazone.get_domain(
            identifier=domain_identifier
        )
        return response

    except ClientError as e:
        print(f"AWS ClientError: {e}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None



def create_project(domain_id):
    target_name = 'engage_ai_project'

    # List existing projects in the domain
    response = datazone.list_projects(domainIdentifier=domain_id)

    for project in response.get('items', []):
        if project.get('name') == target_name:
            project_id = project.get('id')
            print(f"[ℹ] Project '{target_name}' already exists with ID: {project_id}")
            return project_id

    # Create a new project — minimal version
    response = datazone.create_project(
        domainIdentifier=domain_id,
        name=target_name,
        description='Project for managing Engage AI raw data and indicator assets'
    )
    project_id = response['id']
    print(f"[✔] Project created: {project_id}")
    return project_id

############ Create ################
def create_blueprint(domain_id: str, blueprint_id: str, provisioning_role_arn: str) -> None:

    response = datazone.put_environment_blueprint_configuration(
        domainIdentifier=domain_id,
        environmentBlueprintIdentifier=blueprint_id,
        enabledRegions=[region_name],  # must be list
        provisioningRoleArn=provisioning_role_arn
        # provisioningConfigurations omitted here - add if needed and valid
    )
    print(f"Configured blueprint '{blueprint_id}' in domain '{domain_id}'.")


def create_environment_profile(domain_id: str, project_id: str, blueprint_id: str,
                               profile_name: str = "Engage_AI_Profile",
                               description: str = "Profile for Engage AI environment") -> str:
    response = datazone.create_environment_profile(
        domainIdentifier=domain_id,
        name=profile_name,
        description=description,
        projectId=project_id,
        blueprintId=blueprint_id
    )
    env_profile_id = response['id']
    print(f"Created environment profile '{profile_name}' with id: {env_profile_id}")
    return env_profile_id

def create_environment(domain_id: str, project_id: str, env_profile_id: str,
                       environment_name: str = "Engage_AI_Environment",
                       description: str = "Engage AI environment to host data products") -> str:
    response = datazone.create_environment(
        domainIdentifier=domain_id,
        projectId=project_id,
        environmentProfileId=env_profile_id,
        name=environment_name,
        description=description
    )
    env_id = response['id']
    print(f"Created environment '{environment_name}' with id: {env_id}")
    return env_id


def create_data_source(domain_id: str, project_id: str, env_id: str,
                       data_source_name: str, glue_db_name: str, glue_role_arn: str) -> str:
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
    print(f"Created data source '{data_source_name}' with id: {data_source_id}")
    return data_source_id


############### GET ###############


# def get_blueprints():
#     response = datazone.list_environment_blueprints()
#     blueprints = response.get('items', [])
#     for bp in blueprints:
#         print(f"Blueprint Name: {bp['name']}, Blueprint ID: {bp['id']}")
#     return blueprints

# def get_environments(domain_id):
#     response = datazone.list_environments(domainIdentifier=domain_id)
#     environments = response.get('items', [])
#     for env in environments:
#         print(f"Environment Name: {env['name']}, Environment ID: {env['id']}")
#     return environments

# print("Listing Blueprints:")
# blueprints = get_blueprints()

# print("\nListing Environments:")
# domain_id = create_domain()
# environments = get_environments(domain_id)
# print(environments)



def get_environment_id(domain_id, env_name):

    # List environments in the domain (paginated if needed)
    paginator = datazone.get_paginator('list_environments')
    for page in paginator.paginate(domainIdentifier=domain_id):
        environments = page.get('environments', [])
        for env in environments:
            if env.get('name') == env_name:
                return env.get('id')

    # If not found
    return None

def list_environments(domain_id):
    environments = []
    paginator = datazone.get_paginator('list_environments')
    for page in paginator.paginate(domainIdentifier=domain_id):
        environments.extend(page.get('environments', []))
    return environments


def list_environment_blueprints(domain_id):
    response = datazone.list_environment_blueprints(
        domainIdentifier=domain_id,
        maxResults=50  # adjust as needed
    )
    blueprints = response.get('items', [])
    for bp in blueprints:
        print(f"Blueprint ID: {bp.get('id')}, Name: {bp.get('name')}")
    return blueprints

def get_environment_blueprint(domain_id, blueprint_id):
    response = datazone.get_environment_blueprint(
        domainIdentifier=domain_id,
        environmentBlueprintIdentifier=blueprint_id
    )
    print(f"Blueprint details for ID {blueprint_id}:")
    print(response)
    return blueprint_id


# def list_environment_blueprint_configurations(domain_id):
#     response = datazone.list_environment_blueprint_configurations(
#         domainIdentifier=domain_id,
#         maxResults=50  # optional, max items per page
#     )
#     configs = response.get('items', [])
#     blueprint_id=config.get('environmentBlueprintId')

#     for config in configs:
#         print(f"Blueprint ID: {config.get('environmentBlueprintId')}, Regions: {config.get('enabledRegions')}")
#     return blueprint_id


def list_environment_blueprint_configurations(domain_id):
    response = datazone.list_environment_blueprint_configurations(domainIdentifier=domain_id)
    configs = response.get('items', [])

    if not configs:
        print("No environment blueprint configurations found.")
        return None

    # If you expect multiple configs, handle accordingly. For now, take the first one:
    config = configs[0]  # This guarantees config is assigned

    blueprint_id = config.get('environmentBlueprintId')
    print(f"Found blueprint id: {blueprint_id}")
    return blueprint_id

############################################################


def create_environment_profile(domain_id):
    profile_name = "engage_ai_env_profile"

    # Check if profile exists first (optional)
    profiles = datazone.list_environment_profiles(domainIdentifier=domain_id).get('items', [])
    for p in profiles:
        if p['name'] == profile_name:
            print(f"Environment Profile '{profile_name}' exists with ID: {p['id']}")
            return p['id']

    # Create environment profile
    response = datazone.create_environment_profile(
        domainIdentifier=domain_id,
        name=profile_name,
        description="Environment profile for Engage AI",
        provisioningRoleArn="arn:aws:iam::184898280326:role/datazone-provisioning-role",  # Replace with your provisioning role ARN
        userParameters=[]  # You can add user parameters here if needed
    )
    profile_id = response['id']
    print(f"Created Environment Profile with ID: {profile_id}")
    return profile_id


######

def create_data_resource(domain_id, environment_id):
    data_resource_name = "engage_ai_glue_table"

    # Example Glue data source config - adjust to your setup
    data_source_config = {
        "glueRunConfiguration": {
            "roleArn": "arn:aws:iam::184898280326:role/GlueAccessRole",  # Role with Glue and S3 permissions
            "databaseName": "your_glue_database",
            "tableName": "your_glue_table"
        }
    }

    response = datazone.create_data_resource(
        domainIdentifier=domain_id,
        environmentId=environment_id,
        name=data_resource_name,
        description="Glue table data resource for Engage AI",
        type="GLUE_TABLE",  # or S3_OBJECT, ATHENA_QUERY, etc.
        dataSourceConfiguration=data_source_config,
        # Optionally set other metadata, classification, tags here
    )
    data_resource_id = response['id']
    print(f"Created Data Resource with ID: {data_resource_id}")
    return data_resource_id






####
config_id = ''  # If creating new, use empty string or None
def put_environment_blueprint_configuration(domain_id, blueprint_id, config_id, region_name: str = 'ap-southeast-2'):

    params = {
        'domainIdentifier': domain_id,
        'environmentBlueprintId': blueprint_id,
        'enabledRegions': [region_name]
    }

    # If you have a configuration ID to update, include it
    if config_id:
        params['id'] = config_id

    response = datazone.put_environment_blueprint_configuration(**params)
    return response


##########################################################################################

# domain_id = create_domain()

# project_id = create_project(domain_id)

# # GLUE_DB_NAME = "engage-ai-dataset"
# # # DATAZONE_GLUE_ROLE_ARN = "arn:aws:iam::123456789012:role/AmazonDataZoneGlueAccess-yourdomain"
# # DATAZONE_GLUE_ROLE_ARN = "arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution"
# provisioning_role_arn= "arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution"
# # # Create project
# # # project_id = create_project(domain_id, PROJECT_NAME, description="Engage AI project")
# response = put_environment_blueprint_configuration(domain_id, blueprint_id, config_id, region_name)
# print("PutEnvironmentBlueprintConfiguration response:", response)
# blueprint_id = create_blueprint(domain_id, project_id, provisioning_role_arn)

# # Create environment profile
# env_profile_id = create_environment_profile(domain_id, project_id, blueprint_id)

# # Create environment
# env_id = create_environment(domain_id, project_id, env_profile_id)

# # Create data source for Glue
# data_source_id = create_data_source(
#     domain_id,
#     project_id,
#     env_id,
#     data_source_name="engageai-glue-source",
#     glue_db_name=GLUE_DB_NAME,
#     glue_role_arn=DATAZONE_GLUE_ROLE_ARN
# )



# # def main():
# domain_id = create_domain()
# project_id = create_project(domain_id)
# blueprints = list_environment_blueprints(domain_id)
# print(blueprints)
# blueprint_id = blueprints[0]['id']
# config_id = ''
# region_name = 'ap-southeast-2'

# response = put_environment_blueprint_configuration(domain_id, blueprint_id, config_id, region_name)
# print("PutEnvironmentBlueprintConfiguration response:", response)

# env_profile_id = create_environment_profile(domain_id, project_id, blueprint_id)
# env_id = create_environment(domain_id, project_id, env_profile_id)
# print(f"Environment created with ID: {env_id}")

# if __name__ == "__main__":
#     main()

domain_id = create_domain()
project_id = create_project(domain_id)
member_type = 'ROLE'  # or 'GROUP' or 'ROLE'
member_identifier = 'arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520'  # example IAM user ARN
role = 'CONTRIBUTOR'

blueprint_id=list_environment_blueprint_configurations(domain_id)

 # Example: take first blueprint from list
env_profile_id = create_environment_profile(domain_id)
env_id = create_environment(domain_id, blueprint_id, env_profile_id)
data_resource_id = create_data_resource(domain_id, env_id)

# add_member_to_project(domain_id, project_id, member_type, member_identifier, role)

