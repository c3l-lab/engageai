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
        s3_prefix_key: str,
        account: str,
        region: str
    ) -> datazone.CfnDomain:
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
        aws_account_id=account,
        aws_account_region=region
    )


    # datazone_environment = datazone.CfnEnvironment(
    #     scope, "EngageAIDataZoneEnvironment",
    #     domain_identifier=domain.attr_id,
    #     project_identifier=project.attr_id,
    #     name="MyAthenaEnv",
    #     description="Athena environment created via CDK",
    #     environment_blueprint_identifier="default_athena_environment",
    #     aws_account_id="123456789012",
    #     aws_region="ap-southeast-2",
    #     provisioning_role_arn="arn:aws:iam::123456789012:role/DataZoneProvisioningRole",
    #     environment_role_arn="arn:aws:iam::123456789012:role/DataZoneEnvironmentRole",
    #     user_parameters=[
    #         datazone.CfnEnvironment.UserParameterProperty(
    #             name="glue_database_name",
    #             value="your_db_name"
    #         ),
    #         datazone.CfnEnvironment.UserParameterProperty(
    #             name="s3_location",
    #             value="s3://your-data-bucket/"
    #         ),
    #         datazone.CfnEnvironment.UserParameterProperty(
    #             name="athena_workgroup",
    #             value="primary"
    #         )
    #     ]
    # )
    
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