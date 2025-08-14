from aws_cdk import (
    aws_datazone as datazone,
    aws_iam as iam,
    aws_kms,
    aws_s3 as s3,
    aws_kms
)
from constructs import Construct
from c3l_engageai.config import Environment, config
from typing import Tuple


def create_domain(
        scope: Construct, 
        execution_role: iam.IRole, 
        kms_key: aws_kms.IKey) -> str: 
    domain = datazone.CfnDomain(
        scope, "EngageAiDataZoneDomain",
        name="engageai-datazone-domain",
        description="EngageAI data zone domain",
        domain_execution_role=execution_role.role_arn,
        kms_key_identifier=kms_key.key_arn
    )
    
    # --- Create Environment Blueprint ---
        # --- Blueprint Configuration ---
    blueprint = datazone.CfnEnvironmentBlueprintConfiguration(
        scope,
        "MyBlueprintConfiguration",
        domain_identifier=domain.attr_id,  # replace with your DataZone domain ID
        environment_blueprint_identifier="DefaultDataLake",
        enabled_regions=["ap-southeast-2"],  # example region
        provisioning_role_arn=execution_role.role_arn,
        # Optional: environment role permission boundary
        # environment_role_permission_boundary="arn:aws:iam::123456789012:policy/YourBoundaryPolicy",
        # Optional: manage access role ARN
        # manage_access_role_arn="arn:aws:iam::123456789012:role/YourManageAccessRole",
        # Optional: Lake Formation provisioning config
        provisioning_configurations=[
            datazone.CfnEnvironmentBlueprintConfiguration.ProvisioningConfigurationProperty(
                lake_formation_configuration=datazone.CfnEnvironmentBlueprintConfiguration.LakeFormationConfigurationProperty(
                    location_registration_exclude_s3_locations=[
                 
                    ],
                    location_registration_role=execution_role.role_arn
                )
            )
        ]
    )
    return domain.attr_id

def create_project(scope: Construct, domain_id: str) -> str:  # return project ID string
    project = datazone.CfnProject(
        scope, "EngageAIDataProject",
        domain_identifier=domain_id,
        name="engage-ai-project",
        description="Explore CURR3021 student engagement index via moodle behaviour record in log"
    )
    return project.attr_id


def create_environment_profile(
    scope: Construct,
    domain_id: str,
    project_id: str,
    branch: Environment
) -> str:  # return environment profile ID string
    profile = datazone.CfnEnvironmentProfile(
        scope, "DataZoneEnvironmentProfile",
        domain_identifier=domain_id,
        name="data-lake-profile",
        description="Environment profile for data lake operations",
        project_identifier=project_id,
        environment_blueprint_identifier="DefaultDataLake",
        aws_account_id= config.environment_accounts[branch].id,
        aws_account_region= config.environment_accounts[branch].region
    )
    return profile.attr_id



def create_environment(
    scope: Construct,
    domain_id: str,
    project_id: str,
    environment_profile_id: str,
    branch: Environment,
    execution_role: iam.IRole, 
    name: str = "production-data-environment",
    description: str = "Production environment for engage_ai data operations"
) -> str: 
    env = datazone.CfnEnvironment(
        scope, "EngageAIDataZoneEnvironment",
        domain_identifier=domain_id,
        environment_profile_identifier=environment_profile_id,
        name=name,
        description=description,
        project_identifier=project_id,
        environment_account_identifier=config.environment_accounts[branch].id,
        environment_account_region=config.environment_accounts[branch].region,
        environment_role_arn= execution_role.role_arn
    )
    return env.attr_id

# def create_s3_data_source(
#     scope: Construct,
#     domain_id: str,
#     environment_id: str,
#     project_id: str
# ) -> str:  # return data source ID string
#     data_source = datazone.CfnDataSource(
#         scope, "S3DataSource",
#         domain_identifier=domain_id,
#         environment_identifier=environment_id,
#         name="direct-s3-data-source",
#         project_identifier=project_id,
#         type="S3",
#         description="Direct S3 data source for third-party data sharing",
#         configuration={},
#         enable_setting="ENABLED",
#         publish_on_import=False,
#         recommendation=datazone.CfnDataSource.RecommendationConfigurationProperty(
#             enable_business_name_generation=True
#         )
#     )
#     return data_source.attr_id

def create_glue_data_source(
    scope: Construct,
    execution_role:iam.IRole, 
    domain_id: str,
    environment_id: str,
    project_id: str
) -> str:
    data_source = datazone.CfnDataSource(
        scope, "GlueDataSource",
        domain_identifier=domain_id,
        environment_identifier=environment_id,
        project_identifier=project_id,
        name="engage_ai_dataset",
        description="Import existing Glue Data Catalog tables",
        type="GLUE",  # must be "GLUE"
        configuration=datazone.CfnDataSource.DataSourceConfigurationInputProperty(
            glue_run_configuration=datazone.CfnDataSource.GlueRunConfigurationInputProperty(
                catalog_name="AwsDataCatalog",
                data_access_role=execution_role.role_arn,
                relational_filter_configurations=[
                    datazone.CfnDataSource.RelationalFilterConfigurationProperty(
                        database_name='engage_ai_dataset',
                        filter_expressions=[
                            datazone.CfnDataSource.FilterExpressionProperty(
                                expression="*",
                                type="INCLUDE",
                            )
                        ]
                    )
                ]
            )
        ),
        enable_setting="ENABLED",
        publish_on_import=False,
        recommendation=datazone.CfnDataSource.RecommendationConfigurationProperty(
            enable_business_name_generation=True
        ),
        # You can add a schedule if you want it to run periodically:
        schedule=datazone.CfnDataSource.ScheduleConfigurationProperty(
            schedule="cron(0 1 * * ? *)",
            timezone="AUSTRALIA_MELBOURNE"
        ),
    )
    return data_source.attr_id


    # data_source = datazone.CfnDataSource(
    #     scope, "GlueDataSource",
    #     domain_identifier=domain_id,
    #     environment_identifier=environment_id,
    #     project_identifier=project_id,
    #     name="enagge_ai_dataset",
    #     description= "Glue catalog data source",
    #     type="GLUE_CATALOG",  # Confirm the exact type string
    #     configuration={
    #         "GlueTable": {
    #             "DatabaseName": "engage_ai glue database name",
    #             "TableName": "engage_ai glue table name"
    #         }
    #     },
    #     enable_setting="ENABLED",
    #     publish_on_import=False,
    #     recommendation=datazone.CfnDataSource.RecommendationConfigurationProperty(
    #         enable_business_name_generation=True
    #     )
    # )
    # return data_source.attr_id
