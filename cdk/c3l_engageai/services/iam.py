from aws_cdk import (
    aws_iam,
    aws_iam as iam,
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

def create_datazone_execution_role(
    scope: Construct, 
    datazone_kms_key: aws_kms.Key,
    data_bucket: aws_s3.Bucket
) -> aws_iam.Role:
    return iam.Role(
        scope, "DataZoneDomainExecutionRole",
        assumed_by=iam.ServicePrincipal("datazone.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonDataZoneServiceRolePolicy")
        ],
        inline_policies={
            "DataZoneS3Access": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:DeleteObject",
                            "s3:ListBucket",
                            "s3:GetBucketLocation"
                        ],
                        resources=[
                            data_bucket.bucket_arn,
                            f"{data_bucket.bucket_arn}/*"
                        ]
                    ),
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "kms:Decrypt",
                            "kms:DescribeKey",
                            "kms:Encrypt",
                            "kms:GenerateDataKey*",
                            "kms:ReEncrypt*"
                        ],
                        resources=[datazone_kms_key.key_arn]
                    )
                ]
            )
        }
    )

