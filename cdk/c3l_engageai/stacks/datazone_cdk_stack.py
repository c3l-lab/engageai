from aws_cdk import (
    Stack,
    aws_datazone as datazone,
    aws_iam as iam,
    aws_glue as glue
)
from constructs import Construct

class DatazoneCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Execution Role
        execution_role = iam.Role(
            self, "DataZoneExecutionRole",
            assumed_by=iam.ServicePrincipal("datazone.amazonaws.com"),
               managed_policies=[
                # S3 Access
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSGlueConsoleFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSGlueServiceRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAthenaFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDataZoneFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLakeFormationDataAdmin")
            ]
        )

        # 2. Domain
        domain = datazone.CfnDomain(
            self, "EngageAiDataZoneDomain",
            name="engageai-datazone-domain",
            description="EngageAI data zone domain",
            domain_execution_role=execution_role.role_arn,
            kms_key_identifier="alias/aws/datazone"
        )

        # 3. Project
        project = datazone.CfnProject(
            self, "EngageAIDataProject",
            domain_identifier=domain.attr_id,
            name="engage-ai-project",
            description="Explore CURR3021 student engagement index via moodle behaviour record in log"
        )

        # S3 Asset Source
        s3_asset_source = datazone.CfnAssetSource(
            self, "S3AssetSource",
            domain_identifier=domain.attr_id,
            name="s3-azure-ingested-data",
            asset_source_type="S3",
            configuration={
                "s3Configuration": {
                    "bucket": "engage-ai-dataset",         # ✅ your real bucket name
                    "keyPrefix": "engageai_indicator/"     # ✅ optional folder path
                }
            }
        )
        # glue_db = glue.CfnDatabase(
        #     self, "EngageAIGlueDatabase",
        #     catalog_id=self.account,
        #     database_input={
        #         "name": "azure_s3_catalog"
        #     }
        # )

        # # 4. Asset Source (Glue)
        # asset_source = datazone.CfnAssetSource(
        #     self, "EngageeAIGlueAssetSource",
        #     domain_identifier=domain.attr_id,
        #     name="engageai-glue-data-catalog",
        #     asset_source_type="GLUE",
        #     configuration={
        #         "glueConfiguration": {
        #             "catalog": "AwsDataCatalog",
        #             "database": "azure_s3_catalog"
        #         }
        #     }
        # )
