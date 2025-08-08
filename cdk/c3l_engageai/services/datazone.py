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
    # S3 Asset Source
    s3_asset_source = datazone.CfnAssetSource(
        scope, "S3AssetSource",
        domain_identifier=domain.attr_id,
        name="s3-azure-ingested-data",
        asset_source_type="S3",
        configuration={
            "s3Configuration": {
                "bucket": s3_bucket.bucket_name,  # ✅ your real bucket name
                "keyPrefix": s3_prefix_key        # ✅ optional folder path
            }
        }
    )
    return domain, project

    