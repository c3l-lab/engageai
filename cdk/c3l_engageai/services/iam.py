from aws_cdk import (
    aws_iam,
    aws_s3,
    aws_kms
)
from constructs import Construct

from c3l_engageai.config import Environment
from c3l_engageai.helpers import resource_name
from typing import cast


def create_lambda_default_execution_role(
    scope: Construct, branch: Environment, stack_name: str
) -> aws_iam.Role:
    role_name = resource_name("lambda-execution-role", branch)
    lambda_default_execution_role = aws_iam.Role(
        scope,
        "LambdaDefaultExecutionRole",
        assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),  # type: ignore
        managed_policies=[
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
            # aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            #     "service-role/AWSLambdaVPCAccessExecutionRole"
            # ),
        ],
        description=("Lambda Role to access basic execution permissions"),
        role_name=role_name,
    )

    lambda_default_execution_role.add_to_policy(
        aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "lambda:InvokeFunction",
                "lambda:InvokeFunctionUrl",
                "logs:*",
                "secretsmanager:*",
                "states:*",
                "sagemaker:*",
                "ecr:*",
                "s3:*",
                "iam:*",
                "ses:*"
            ],
            resources=["*"],
        )
    )

    return lambda_default_execution_role

def create_sagemaker_default_execution_role(
    scope: Construct, branch: Environment, stack_name: str
) -> aws_iam.Role:
    lambda_default_execution_role = aws_iam.Role(
        scope,
        "SagemakerDefaultExecutionRole",
        assumed_by=aws_iam.ServicePrincipal("codepipeline.amazonaws.com"),  # type: ignore
        description=("Lambda Role to access basic execution permissions"),
        role_name=resource_name(stack_name + "sagemaker-default-execution-role", branch),
    )

    lambda_default_execution_role.add_to_policy(
        aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "kms:*",
                "s3:*"
            ],
            resources=["*"],
        )
    )
    return lambda_default_execution_role


def create_lambda_role(
    scope: Construct, branch: Environment, stack_name: str
) -> aws_iam.Role:
    # Grant S3 permissions
    #pipeline_bucket.grant_read_write(pipeline_role)

    # Create Lambda role
    # type: ignore
    return aws_iam.Role(
        scope, "LambdaRole", # pyright: ignore
        assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"), # pyright: ignore
        managed_policies=[
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSageMakerFullAccess"
            )
        ]
    )

from aws_cdk import aws_iam
from constructs import Construct

def create_datazone_execution_role(
    scope: Construct,
    construct_id: str,
    branch: Environment
) -> aws_iam.IRole:
  
    execution_role = aws_iam.Role(
        scope,
        construct_id,
        role_name=resource_name("datazone-execution-role", branch),
        assumed_by=cast(aws_iam.IPrincipal, aws_iam.ServicePrincipal("datazone.amazonaws.com")),
        managed_policies=[
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonS3FullAccess"
            ),
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSGlueServiceRole"
            ),
        ],
    )

    # --- KMS Permissions ---
    execution_role.add_to_policy(
        aws_iam.PolicyStatement(
            sid="KMSBasic",
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "kms:Decrypt",
                "kms:Encrypt",
                "kms:PutKeyPolicy",
                "kms:GenerateDataKey",
            ],
            resources=["*"],
        )
    )

    # --- DataZone Management Permissions ---
    execution_role.add_to_policy(
        aws_iam.PolicyStatement(
            sid="DataZoneManageEnv",
            effect=aws_iam.Effect.ALLOW,
            actions=["datazone:*"],
            resources=["*"],
        )
    )

    # --- Glue + Lake Formation Permissions ---
    execution_role.add_to_policy(
        aws_iam.PolicyStatement(
            sid="GlueLakeFormationAccess",
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "glue:GetDatabase",
                "glue:GetDatabases",
                "glue:GetTable",
                "glue:GetTables",
                "glue:SearchTables",
                "lakeformation:GetDataAccess",
                "lakeformation:GrantPermissions",
                "lakeformation:RevokePermissions",
                "lakeformation:GetResourceLFTags",
                "lakeformation:ListResources",
            ],
            resources=["*"],
        )
    )

    return cast(aws_iam.IRole, execution_role)

def create_glue_crawler_role(scope: Construct, branch: Environment) -> aws_iam.Role:
    crawler_role = aws_iam.Role(
        scope, "GlueCrawlerRole",
        assumed_by=cast(aws_iam.IPrincipal, aws_iam.ServicePrincipal("glue.amazonaws.com")),
        role_name=resource_name("glue-crawler", branch),
        managed_policies=[
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
        ]
    )

    crawler_role.add_to_policy(
        aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "lambda:InvokeFunction",
                "lambda:InvokeFunctionUrl",
                "logs:*",
                "secretsmanager:*",
                "states:*",
                "ecr:*",
                "s3:*",
                "iam:*",
                "ses:*",
                "athena:*",
                "glue:*",
                "lakeformation:*",
                "kms:*",
                "sts:*"
            ],
            resources=["*"],
        )
    )
    return crawler_role

def setup_lakeformation_access(scope: Construct, branch: Environment):
    # Create a new role that grants the permissions we need
    kms_access_role = aws_iam.Role(
        scope,
        "LakeFormationKMSRole",
        role_name=resource_name(f"LakeFormationKMSAccess",branch),
        description=f"Role for Lake Formation KMS access ({branch})",
        # Allow the SSO role to assume this role
        assumed_by=cast(
            aws_iam.IPrincipal, 
            aws_iam.ArnPrincipal("arn:aws:iam::184898280326:role/aws-service-role/lakeformation.amazonaws.com/AWSServiceRoleForLakeFormationDataAccess")
        )
    )
    # Add the KMS permissions to this new role
    kms_access_role.add_to_policy(
        aws_iam.PolicyStatement(
            sid="KMSAccess",
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "kms:Decrypt",
                "kms:DescribeKey",
                "kms:Encrypt",
                "kms:GenerateDataKey*",
                "kms:ReEncrypt*"
            ],
            resources=["*"],
        )
    )
