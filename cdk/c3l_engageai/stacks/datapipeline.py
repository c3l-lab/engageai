from aws_cdk import (
    core,
    aws_s3,
    aws_iam as iam,
    aws_lambda as _lambda,
    custom_resources as cr,
    Stack
)

from constructs import Construct

from c3l_engageai.config import Environment
from c3l_engageai.services.secretsmanager import create_secrets
from c3l_engageai.services.iam import create_lambda_default_execution_role
from c3l_engageai.services.lambdas import (
    create_shared_lambda_layer,
    create_lambda_athena_query
)
from c3l_engageai.services.datazone import (
    create_datazone
)
from c3l_engageai.services.iam import (
    create_datazone_execution_role
)


class Datapipeline(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Create S3 + KMS
        bucket = s3.Bucket.from_bucket_name(
            self, "EngageAiDatasetBucket",
            bucket_name="engage-ai-dataset"
        )
        kms_key = kms.Key(self, "DataZoneKey")

        # 2. Create Execution Role
        execution_role = create_datazone_execution_role(self, kms_key, bucket)

        # 3. Create Domain
        domain_cr = cr.AwsCustomResource(
            self, "CreateDataZoneDomain",
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=[
                        "datazone:CreateDomain",
                        "datazone:GetDomain"
                    ],
                    resources=["*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="DataZone",
                action="createDomain",
                parameters={
                    "name": "engage_ai_datazone",
                    "description": "DataZone domain for Engage AI project",
                    "domainExecutionRole": execution_role.role_arn,
                    "kmsKeyIdentifier": kms_key.key_arn
                },
                physical_resource_id=cr.PhysicalResourceId.from_response("id")
            )
        )
        domain_id = domain_cr.get_response_field("id")

        # 4. Create Project
        project_cr = cr.AwsCustomResource(
            self, "CreateDataZoneProject",
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=[
                        "datazone:CreateProject",
                        "datazone:GetProject"
                    ],
                    resources=["*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="DataZone",
                action="createProject",
                parameters={
                    "domainIdentifier": domain_id,
                    "name": "engage_ai_project",
                    "description": "Project for managing Engage AI raw data and indicator assets"
                },
                physical_resource_id=cr.PhysicalResourceId.from_response("id")
            )
        )
        project_id = project_cr.get_response_field("id")
        project_cr.node.add_dependency(domain_cr)

        # 5. Create Blueprint
        blueprint_cr = cr.AwsCustomResource(
            self, "CreateDataZoneBlueprint",
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["datazone:CreateBlueprint", "datazone:GetBlueprint"],
                    resources=["*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="DataZone",
                action="createBlueprint",
                parameters={
                    "domainIdentifier": domain_id,
                    "name": "MyDefaultBlueprint",
                    "description": "Default environment blueprint created via CDK",
                    "enabled": True
                },
                physical_resource_id=cr.PhysicalResourceId.from_response("id")
            )
        )
        blueprint_id = blueprint_cr.get_response_field("id")
        blueprint_cr.node.add_dependency(project_cr)

        # 6. Create Environment Profile
        profile_cr = cr.AwsCustomResource(
            self, "CreateDataZoneProfile",
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["datazone:CreateEnvironmentProfile", "datazone:GetEnvironmentProfile"],
                    resources=["*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="DataZone",
                action="createEnvironmentProfile",
                parameters={
                    "domainIdentifier": domain_id,
                    "name": "MyEnvProfile",
                    "description": "Profile for environment",
                    "environmentBlueprintIdentifier": blueprint_id,
                    "userParameters": [
                        {"name": "ExecutionRoleArn", "value": execution_role.role_arn}
                    ]
                },
                physical_resource_id=cr.PhysicalResourceId.from_response("id")
            )
        )
        profile_id = profile_cr.get_response_field("id")
        profile_cr.node.add_dependency(blueprint_cr)

        # 7. Create Environment
        env_cr = cr.AwsCustomResource(
            self, "CreateDataZoneEnvironment",
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["datazone:CreateEnvironment"],
                    resources=["*"]
                )
            ]),
            on_create=cr.AwsSdkCall(
                service="DataZone",
                action="createEnvironment",
                parameters={
                    "domainIdentifier": domain_id,
                    "projectIdentifier": project_id,
                    "name": "MyEnvFromBlueprint",
                    "description": "Environment created from default blueprint",
                    "environmentBlueprintIdentifier": blueprint_id,
                    "environmentProfileIdentifier": profile_id,
                    "userParameters": [
                        {"name": "ExecutionRoleArn", "value": execution_role.role_arn}
                    ]
                },
                physical_resource_id=cr.PhysicalResourceId.of("MyEnvFromBlueprint")
            )
        )
        env_cr.node.add_dependency(profile_cr)




