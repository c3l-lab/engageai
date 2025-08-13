from aws_cdk import (
    aws_datazone as datazone,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms
)
from constructs import Construct
from typing import Tuple


def create_domain(
        scope: Construct, 
        execution_role: iam.IRole, 
        kms_key: aws_kms.IKey) -> datazone.CfnDomain:
    domain = datazone.CfnDomain(
        scope, "EngageAiDataZoneDomain",
        name="engageai-datazone-domain",
        description="EngageAI data zone domain",
        domain_execution_role=execution_role.role_arn,
        kms_key_identifier=kms_key.key_id
    )
    return domain

def create_project(scope: Construct, domain: datazone.CfnDomain) -> datazone.CfnProject:
    project = datazone.CfnProject(
        scope, "EngageAIDataProject",
        domain_identifier=domain.attr_id,
        name="engage-ai-project",
        description="Explore CURR3021 student engagement index via moodle behaviour record in log"
    )
    return project


def create_environment_profile(
    scope: Construct,
    domain: datazone.CfnDomain,
    project: datazone.CfnProject,
    account: str,
    region: str
) -> datazone.CfnEnvironmentProfile:
    profile = datazone.CfnEnvironmentProfile(
        scope, "DataZoneEnvironmentProfile",
        domain_identifier=domain.attr_id,
        environment_blueprint_identifier="DefaultDataLake",
        name="data-lake-profile",
        description="Environment profile for data lake operations",
        project_identifier=project.attr_id,
        aws_account_id=account,
        aws_account_region=region
    )
    return profile


def create_environment(
    scope: Construct,
    domain: datazone.CfnDomain,
    project: datazone.CfnProject,
    environment_profile: datazone.CfnEnvironmentProfile,
    name: str = "production-data-environment",
    description: str = "Production environment for engage_ai data operations"
) -> datazone.CfnEnvironment:
    env = datazone.CfnEnvironment(
        scope, "EngageAIDataZoneEnvironment",
        domain_identifier=domain.attr_id,
        environment_profile_identifier=environment_profile.attr_id,
        name=name,
        description=description,
        project_identifier=project.attr_id
    )
    return env


def create_s3_data_source(
    scope: Construct,
    domain: datazone.CfnDomain,
    environment: datazone.CfnEnvironment,
) -> datazone.CfnDataSource:
    data_source = datazone.CfnDataSource(
        scope, "S3DataSource",
        domain_identifier=domain.attr_id,
        environment_identifier=environment.attr_id,
        name="direct-s3-data-source",
        project_identifier=domain.attr_id,
        type="S3",
        description="Direct S3 data source for third-party data sharing",
        # If config is empty, you can omit or pass empty dict
        configuration=datazone.CfnDataSource.DataSourceConfigurationInputProperty(
            # No Glue crawler config for direct S3 access
        ),
        enable_setting="ENABLED",
        publish_on_import=False,
        recommendation=datazone.CfnDataSource.RecommendationConfigurationProperty(
            enable_business_name_generation=True
        )
    )
    return data_source
