from aws_cdk import (
    Stack,
    aws_datazone as datazone,
    aws_iam as iam,
    aws_s3,
    aws_glue as glue
)
from constructs import Construct

def create_datazone(
        scope: Construct, 
        execution_role: iam.IRole,
        s3_bucket: aws_s3.IBucket,
        s3_prefix_key: str) -> datazone.CfnDomain:
    # 2. Domain
    domain = datazone.CfnDomain(
        scope, "EngageAiDataZoneDomain",
        name="engageai-datazone-domain",
        description="EngageAI data zone domain",
        domain_execution_role=execution_role.role_arn,
        kms_key_identifier="alias/aws/datazone"
    )

    # 3. Project
    project = datazone.CfnProject(
        scope, "EngageAIDataProject",
        domain_identifier=domain.attr_id,
        name="engage-ai-project",
        description="Explore CURR3021 student engagement index via moodle behaviour record in log"
    )    
    
    # Create DataZone Environment Profile
    environment_profile = datazone.CfnEnvironmentProfile(
        scope, "DataZoneEnvironmentProfile",
        domain_identifier=domain.attr_id,
        environment_blueprint_identifier="DefaultDataLake",
        name="data-lake-profile",
        description="Environment profile for data lake operations",
        project_identifier=project.attr_id,
        # aws_account_id=self.account,
        # aws_account_region=self.region
    )
    
    # Create DataZone Environment
    datazone_environment = datazone.CfnEnvironment(
        scope, "DataZoneEnvironment",
        domain_identifier=domain.attr_id,
        environment_profile_identifier=environment_profile.attr_id,
        name="production-data-environment",
        description="Production environment for data operations",
        project_identifier=project.attr_id
    )

    # Create Data Source for direct S3 access (no Glue crawler)
    data_source = datazone.CfnDataSource(
        scope, "S3DataSource",
        domain_identifier=domain.attr_id,
        environment_identifier=datazone_environment.attr_id,
        name="direct-s3-data-source",
        project_identifier=domain.attr_id,
        type="S3",
        description="Direct S3 data source for third-party data sharing",
        configuration=datazone.CfnDataSource.DataSourceConfigurationInputProperty(
            # Using S3 configuration instead of Glue
            # DataZone will handle S3 objects directly
        ),
        enable_setting="ENABLED",
        publish_on_import=False,  # Manual publishing for direct S3 control
        recommendation=datazone.CfnDataSource.RecommendationConfigurationProperty(
            enable_business_name_generation=True
        )
        # Removed automatic schedule - manual control for direct S3 sharing
    )
    return domain, project