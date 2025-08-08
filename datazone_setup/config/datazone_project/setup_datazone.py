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
# def create_domain():
#     response = datazone.create_domain(
#         name='engage_ai_datazone',
#         description='DataZone domain for Engage AI project',
#         domainExecutionRole='arn:aws:iam::184898280326:role/service-role/AmazonDataZoneDomainExecution',
#         kmsKeyIdentifier='arn:aws:kms:ap-southeast-2:184898280326:key/cfcbd85c-6eb3-47c4-b5e5-2dca0fce71c4'
#     )
#     domain_id = response['id']
#     print(f"[✔] Domain created: {domain_id}")
#     return domain_id

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


def get_datazone_domain_id(domain_identifier: str, profile_name: str = 'default', region: str = 'ap-southeast-2') -> str:
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        datazone = session.client('datazone')

        response = datazone.get_domain(identifier=domain_identifier)
        return response.get('id')  # Only return the domain ID

    except ClientError as e:
        print(f"AWS ClientError: {e}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None


# domain_id = "dzd_43w640c69o98rm"  # replace with your real domain ID
# domain_id = create_domain()
# details = get_datazone_domain_details(domain_id, profile_name='c3l-analytics')
# if details:
#     print("Domain details:")
#     print(details)
# id_domain=get_datazone_domain_id(domain_id, profile_name='c3l-analytics')
# print(id_domain)



############################## ---------- Create Glossary Term----------  ############################## 

# import os
# import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# print(sys.path)

# from datazone_setup.config.datazone_project.setup_glossary import get_or_create_glossary, get_or_create_glossary_term
# # term_name = "Student_Engagement_Indicator"
# # term_description = "Glossary term describing student engagement indicators"

# domain_id = create_domain()

# glossary_name = 'MainGlossary'
# glossary_description = 'Glossary for Engage_AI indicators and all dataset'
# glossary_id = get_or_create_glossary(domain_id,glossary_name, glossary_description, profile_name, region_name)
# print(f"Using glossary term ID: {glossary_id}")

# term_name='Student_Engagement_Indicator'
# term_description='Describes student engagement levels with Indicator'
# # Create or get term
# if glossary_id:
#     term_id = get_or_create_glossary_term(domain_id, glossary_id, term_name,term_description, profile_name, region_name)
#     print(f"Using glossary term ID: {term_id}")


### ---------- Step 2: Create Project ----------
# def create_project(domain_id):
#     response = datazone.create_project(
#         domainIdentifier=domain_id,
#         name='engage_ai_project',
#         description='Project for managing Engage AI raw data and indicator assets',
#         glossaryTerms=[],
#         userParameters=[]
#     )
#     project_id = response['id']
#     print(f"[✔] Project created: {project_id}")
#     return project_id

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

domain_id = create_domain()
# time.sleep(3)

# terms = list_glossary_terms(domain_id, profile_name='c3l-analytics')
# print(terms)

project_id = create_project(domain_id)
print(project_id)


### ---------- Step 3a: Register Glue Asset Source ----------
def register_glue_asset_source(domain_id):
    response = datazone.create_asset_source(
        domainIdentifier=domain_id,
        name='glue_catalog_engageai_source',
        description='Glue data catalog asset source for Engage_ai',
        assetSourceType='GLUE',
        configuration={
            'glueConfiguration': {
                'catalog': 'AwsDataCatalog',
                'database': '<your-glue-database>'
            }
        }
    )
    asset_source_id = response['id']
    print(f"[✔] Glue asset source registered: {asset_source_id}")
    return asset_source_id


### ---------- Step 3b: Register S3 Asset Source ----------


# def register_s3_asset(domain_id, project_id):
#     response = datazone.create_asset(
#         domainIdentifier=domain_id,
#         projectIdentifier=project_id,
#         name='engageai_s3_asset',
#         typeIdentifier='S3',
#         typeRevision='1',
#         description='S3 bucket for Engage_AI processed assets',
#         predictionConfiguration={
#             'enabled': False
#         },
#         externalIdentifier='engageai_indicator_dataset',
#         resourceMetadata={
#             's3': {
#                 'bucket': 'engage-ai-dataset',
#                 'key': 'engageai_indicator/'  # folder path inside bucket
#             }
#         }
#     )

#     asset_id = response.get('id')
#     print(f"[✔] Created S3 asset with ID: {asset_id}")
#     return asset_id


import boto3

def register_s3_asset_source(domain_id, project_id):

    # Optional: check if asset source already exists to avoid duplication
    source_name = 'engageai_s3_source'
    
    # Register the S3 bucket as an asset source
    try:
        response = datazone.create_asset_source(
            domainIdentifier=domain_id,
            name=source_name,
            description='S3 asset source for Engage AI project',
            projectIdentifier=project_id,
            assetSourceType='S3',
            configuration={
                's3AssetSourceConfiguration': {
                    'bucket': 'engage-ai-dataset',
                    'keyPrefix': 'engageai_indicator/'  # Optional path inside bucket
                }
            }
        )
        source_id = response['id']
        print(f"✅ S3 asset source registered with ID: {source_id}")
        return source_id
    except Exception as e:
        print("❌ Failed to register S3 asset source:", str(e))
        return None


# def register_s3_asset(domain_id, project_id,asset_name='Engage_AI indicator index from S3'):

#     metadata_forms = [
#         {
#             "formName": "AssetMetadataForm",
#             "content": json.dumps({  # Convert to JSON string
#                 "description": "Engage_AI S3 Data asset registered via script",
#                 "assetOwner": "Engage_ai_c3l_team",
#                 "sensitivity": "Confidential"
#             })
#         }
#     ]
#     # Create the asset
#     try:
#         response = datazone.create_asset(
#             domainIdentifier=domain_id,
#             name=asset_name,
#             typeIdentifier='S3',
#             typeRevision='1',
#             owningProjectIdentifier=project_id,
#             externalIdentifier='s3:/engage-ai-dataset/engageai_indicator/',
#             description='Cleaned data converted into indicator index from S3 bucket',
#             formsInput=metadata_forms
#         )
#         print("✅ Asset registered successfully.")
#         return response

#     except Exception as e:
#         print("❌ Failed to register asset:", str(e))
#         return None

    # response = datazone.create_asset(
    #     domainIdentifier=domain_id,
    #     owningProjectIdentifier=project_id,
    #     name='engageai_s3_asset_source',
    #     typeIdentifier='S3',
    #     typeRevision='1',
    #     description='S3 bucket for Engage_AI processed assets',
    #     formsInput=[
    #         {
    #             'formName': 'S3EngageAIAssetForm',  # replace with your actual form name
    #             'content': json.dumps({
    #                 'bucket': 'engage-ai-dataset',
    #                 'key': 'engageai_indicator/',  # optional
    #                 # add additional fields depending on your form definition
    #             })
    #         }
    #     ]
    # )
    # asset_id = response['id']
    # print(f"[✔] Created S3 asset, ID: {asset_id}")
    # return asset_id




    # response = datazone.create_asset(
    #     domainIdentifier=domain_id,
    #     projectIdentifier=project_id,
    #     name='engageai_s3_asset_source',
    #     typeIdentifier='S3',
    #     typeRevision='1',
    #     description='S3 bucket for Engage_AI processed assets',
    #     predictionConfiguration={
    #         "businessNameGeneration": {
    #             "enabled": False
    #         }
    #     },
    #     externalIdentifier='engageai_indicator_dataset',
    #     resourceMetadata={
    #         's3': {
    #             'bucket': 'engage-ai-dataset',
    #             'key': 'engageai_indicator/'
    #         }
    #     }
    # )

    # asset_id = response['id']
    # print(f"[✔] Created S3 asset, ID: {asset_id}")
    # return asset_id



### ---------- Step 4: Create Environment Profile ----------
def create_environment_profile(domain_id):
    response = datazone.create_environment_profile(
        domainIdentifier=domain_id,
        name='default-env-profile',
        description='Default environment for Engage AI project',
        awsAccountId='<your-account-id>',
        awsRegion='your-region',
        environmentBlueprintIdentifier='default-data-lake',  # or use your custom blueprint
        projectIdentifier='engage_ai_project'
    )
    profile_id = response['id']
    print(f"[✔] Environment profile created: {profile_id}")
    return profile_id


### ---------- Step 5: Create Asset (e.g., from S3) ----------
def create_asset(domain_id, project_id):
    response = datazone.create_asset(
        domainIdentifier=domain_id,
        projectIdentifier=project_id,
        name='student_engagement_index',
        typeIdentifier='S3',
        externalIdentifier='<your-s3-path>',
        description='Engagement Index CSV from Lambda output',
        formsInput=[{
            'formName': 'AssetForm',
            'typeIdentifier': 'S3AssetForm',
            'content': '{"columns": ["student_id", "engagement_score"], "format": "csv"}'
        }]
    )
    asset_id = response['id']
    print(f"[✔] Asset created: {asset_id}")
    return asset_id


### ---------- Step 6: Update Asset ----------
def update_asset(domain_id, asset_id):
    response = datazone.update_asset(
        domainIdentifier=domain_id,
        identifier=asset_id,
        name='student_engagement_index_v2',
        description='Updated version with normalized engagement score',
    )
    print(f"[✔] Asset updated: {asset_id}")
    return asset_id


### ---------- Step 7: Publish Asset ----------
def publish_asset(domain_id, asset_id):
    response = datazone.create_asset_revision(
        domainIdentifier=domain_id,
        identifier=asset_id
    )
    print(f"[✔] Asset published: {asset_id}")
    return asset_id


### ---------- Step 8 (Optional): Search for Assets ----------
def search_assets(domain_id):
    response = datazone.search(
        domainIdentifier=domain_id,
        searchScope='ASSET',
        searchText='engagement'
    )
    print("[✔] Search Results:")
    for hit in response.get('items', []):
        print(f" - {hit['name']} ({hit['id']})")


### ---------- Data Product ----------

def create_data_product(domain_id, project_id, asset_id):
    response = datazone.create_data_product(
        domainIdentifier=domain_id,
        projectIdentifier=project_id,
        name='engageai_data_product',
        description='Contains EngageAI Indicator S3 dataset',
        glossaryTerms=[],
        assetForms=[],
        recommendationConfiguration={
            'enableBusinessNameGeneration': False
        },
        assetIdentifiers=[
            {
                'identifier': asset_id,
                'type': 'ASSET'
            }
        ]
    )

    data_product_id = response.get('id')
    print(f"[✔] Created Data Product with ID: {data_product_id}")
    return data_product_id



# ### ---------- 🚀 RUN THE FULL SETUP ----------
# if __name__ == "__main__":
domain_id = create_domain()
time.sleep(3)

# terms = list_glossary_terms(domain_id, profile_name='c3l-analytics')
# print(terms)

project_id = create_project(domain_id)
print(project_id)
    
    # glue_source_id = register_glue_asset_source(domain_id)
s3_source_id = register_s3_asset_source(domain_id, project_id)
time.sleep(3)
    
    # profile_id = create_environment_profile(domain_id)
    # time.sleep(3)

    # asset_id = create_asset(domain_id, project_id)
    # time.sleep(3)

    # update_asset(domain_id, asset_id)
    # time.sleep(2)

    # publish_asset(domain_id, asset_id)
    # time.sleep(2)

    # search_assets(domain_id)
