from aws_cdk import (
    aws_iam,
    aws_s3,
    aws_kms
)
from constructs import Construct

from c3l_engageai.config import Environment
from c3l_engageai.helpers import resource_name

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

from typing import Tuple

def create_datazone_execution_role(
    scope: Construct,
    branch,  # your Environment type
    stack_name: str,
    domain_execution_role_arn: str,
    domain_kms_key_arn: str,
    dz_provisioning_role_arn: str,
    glue_manage_access_role_arn: str
) -> Tuple[aws_iam.Role, aws_iam.IRole, aws_kms.IKey, aws_iam.IRole, aws_iam.IRole]:
  
    # --- Create the DataZone execution role ---
    execution_role = aws_iam.Role(
        scope,
        f"{stack_name}-DataZoneExecutionRole",
        assumed_by=aws_iam.ServicePrincipal("datazone.amazonaws.com"),
        managed_policies=[
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonS3FullAccess"
            ),
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSGlueServiceRole"
            ),
        ],
    )

    # --- Import existing roles & KMS key ---
    domain_execution_role = aws_iam.Role.from_role_arn(
        scope, "DomainExecutionRole", domain_execution_role_arn
    )
    domain_kms_key = aws_kms.Key.from_key_arn(
        scope, "DomainKmsKey", domain_kms_key_arn
    )
    dz_provisioning_role = aws_iam.Role.from_role_arn(
        scope, "DzProvisioningRole", dz_provisioning_role_arn
    )
    glue_manage_access_role = aws_iam.Role.from_role_arn(
        scope, "GlueManageAccessRole", glue_manage_access_role_arn
    )

    return (
        execution_role,
        domain_execution_role,
        domain_kms_key,
        dz_provisioning_role,
        glue_manage_access_role
    )
