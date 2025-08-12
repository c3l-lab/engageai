import boto3
import time
import os
import json
from botocore.exceptions import ClientError

profile_name= 'c3l-analytics'
region_name='ap-southeast-2'
SESSION = boto3.Session(profile_name='c3l-analytics')  # Replace with your actual profile
datazone = SESSION.client('datazone', region_name='ap-southeast-2')


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


# def get_datazone_domain_id(domain_identifier: str, profile_name: str = 'default', region: str = 'ap-southeast-2') -> str:
#     try:
#         session = boto3.Session(profile_name=profile_name, region_name=region)
#         datazone = session.client('datazone')

#         response = datazone.get_domain(identifier=domain_identifier)
#         return response.get('id')  # Only return the domain ID

#     except ClientError as e:
#         print(f"AWS ClientError: {e}")
#         return None
#     except Exception as e:
#         print(f"General error: {e}")
#         return None

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

# domain_id = "dzd_43w640c69o98rm"  # replace with your real domain ID
# domain_id = create_domain()
# details = get_datazone_domain_details(domain_id, profile_name='c3l-analytics')
# if details:
#     print("Domain details:")
#     print(details)
# id_domain=get_datazone_domain_id(domain_id, profile_name='c3l-analytics')
# print(id_domain)



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


config_id = ''  # If creating new, use empty string or None

# try:
#     response = put_environment_blueprint_configuration(domain_id, blueprint_id, config_id, region_name)
#     print("PutEnvironmentBlueprintConfiguration response:", response)
# except datazone.exceptions.ValidationException as e:
#     print("ValidationException:", e)

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


import boto3

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


# env_id = get_environment_id(domain_id, env_name)
#

domain_id = create_domain()

project_id = create_project(domain_id)

# GLUE_DB_NAME = "engage-ai-dataset"
# # DATAZONE_GLUE_ROLE_ARN = "arn:aws:iam::123456789012:role/AmazonDataZoneGlueAccess-yourdomain"
# DATAZONE_GLUE_ROLE_ARN = "arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution"
provisioning_role_arn= "arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution"
# # Create project
# # project_id = create_project(domain_id, PROJECT_NAME, description="Engage AI project")
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

# if __name__ == "__main__":
#     # Fill in your details here:
# DOMAIN_ID = "your-domain-id"
# PROJECT_NAME = "engage_ai_project"
domain_id = create_domain()

project_id = create_project(domain_id)
    
GLUE_DB_NAME = "engage-ai-dataset"
# DATAZONE_GLUE_ROLE_ARN = "arn:aws:iam::123456789012:role/AmazonDataZoneGlueAccess-yourdomain"
DATAZONE_GLUE_ROLE_ARN = "arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution"

# env_id = get_environment_id(domain_id, env_name)
# env_id = get_env_ids_for_blueprint(domain_id)
#     # Create project
#     # project_id = create_project(domain_id, PROJECT_NAME, description="Engage AI project")

#     # Create blueprint
#     blueprint_id = create_blueprint(domain_id, project_id)

# Create environment profile
# env_profile_id = create_environment_profile(domain_id, project_id, blueprint_id)

# # Create environment
# env_id = create_environment(domain_id, project_id, env_profile_id)

# # Create data source for Glue
# env_id = get_env_ids_for_blueprint(domain_id)
# data_source_id = create_data_source(
#     domain_id,
#     project_id,
#     env_id,
#     data_source_name="engageai-glue-source",
#     glue_db_name=GLUE_DB_NAME,
#     glue_role_arn=DATAZONE_GLUE_ROLE_ARN
# )



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
#     for config in configs:
#         blueprint_id = config.get('environmentBlueprintId')
#         print(f"Blueprint ID: {blueprint_id}, Regions: {config.get('enabledRegions')}")
#     return blueprint_id

def list_environment_blueprint_configurations(domain_id):
    response = datazone.list_environment_blueprint_configurations(
        domainIdentifier=domain_id,
        maxResults=50  # optional, max items per page
    )
    configs = response.get('items', [])
    blueprint_ids = []
    for config in configs:
        blueprint_id = config.get('environmentBlueprintId')
        print(f"Blueprint ID: {blueprint_id}, Regions: {config.get('enabledRegions')}")
        if blueprint_id:
            blueprint_ids.append(blueprint_id)
    return blueprint_ids



blueprint_id = list_environment_blueprint_configurations(domain_id)
print(blueprint_id)
response = put_environment_blueprint_configuration(domain_id, blueprint_id, config_id, region_name)
print(response)

def list_environment_blueprint_configurations(domain_id):
    """
    List environment blueprint configurations for a domain and print their details.
    """
    response = datazone.list_environment_blueprint_configurations(
        domainIdentifier=domain_id,
        maxResults=50  # optional, max items per page
    )
    configs = response.get('items', [])
    for config in configs:
        print(f"Configuration ID: {config.get('id')}, "
              f"Blueprint ID: {config.get('environmentBlueprintId')}, "
              f"Enabled Regions: {config.get('enabledRegions')}")
    return configs

def list_environments(domain_id):
    """
    List all environments in the domain and return them.
    """
    environments = []
    paginator = datazone.get_paginator('list_environments')
    for page in paginator.paginate(domainIdentifier=domain_id):
        environments.extend(page.get('environments', []))
    return environments

def get_env_ids_for_blueprint(domain_id):
    """
    For each environment blueprint configuration, find environment IDs that use its blueprint.
    """
    configs = list_environment_blueprint_configurations(domain_id)
    environments = list_environments(domain_id)

    # Map blueprint ID -> list of env IDs
    blueprint_env_map = {}

    for config in configs:
        blueprint_id = config.get('environmentBlueprintId')
        # Find environments that use this blueprint ID
        env_ids = [env.get('id') for env in environments if env.get('environmentBlueprintId') == blueprint_id]
        blueprint_env_map[blueprint_id] = env_ids

    # Print results
    for blueprint_id, env_ids in blueprint_env_map.items():
        print(f"Blueprint ID {blueprint_id} is used by environment IDs: {env_ids}")

    return blueprint_env_map


# Usage example:
# domain_id = 'dzd_exampledomain123'
# env_ids_map = get_env_ids_for_blueprint(domain_id)

# Create data source for Glue
env_id = get_env_ids_for_blueprint(domain_id)
data_source_id = create_data_source(
    domain_id,
    project_id,
    env_id,
    data_source_name="engageai-glue-source",
    glue_db_name=GLUE_DB_NAME,
    glue_role_arn=DATAZONE_GLUE_ROLE_ARN
)
