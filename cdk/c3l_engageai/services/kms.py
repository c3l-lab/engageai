#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_datazone as datazone,
    aws_s3 as s3,
    aws_iam as iam,
    aws_kms as kms,
    RemovalPolicy,
    Duration
)
from constructs import Construct
import json
from c3l_engageai.helpers import resource_name
from c3l_engageai.config import Environment, config
from typing import cast

def create_datazone_kms(scope: Construct, construct_id: str, branch: Environment) -> kms.Key:
    # Create KMS key for encryption
    key = kms.Key(
        scope, construct_id,
        description="KMS key for DataZone encryption",
        enable_key_rotation=True,
        removal_policy=RemovalPolicy.DESTROY
    )
    kms.Alias(
        scope,
        resource_name("datazone_kms", branch),
        alias_name=resource_name("key", branch),
        target_key=cast(kms.IKey, key),
    )
    return key

def create_datalake_kms(scope: Construct, construct_id: str, branch: Environment):
    # Create KMS Key with alias
    key = kms.Key(
        scope,
        construct_id,
        description=f"KMS key for {branch}",
        enable_key_rotation=True
    )
    # Statement 1: Allow account root full access
    key.add_to_resource_policy(
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            principals=[cast(iam.IPrincipal, iam.ArnPrincipal(f"arn:aws:iam::{config.environment_accounts[branch].id}:root"))],
            actions=["kms:*"],
            resources=["*"]
        )
    )
    # Statement 2: Allow LF Data Access Role specific actions
    key.add_to_resource_policy(
        iam.PolicyStatement(
            sid="AllowLFDataAccessRole",
            effect=iam.Effect.ALLOW,
            principals=[cast(iam.IPrincipal, iam.ArnPrincipal(
                f"arn:aws:iam::{config.environment_accounts[branch].id}:role/aws-service-role/lakeformation.amazonaws.com/AWSServiceRoleForLakeFormationDataAccess"
            ))],
            actions=[
                "kms:Decrypt",
                "kms:Encrypt",
                "kms:GenerateDataKey*"
            ],
            resources=["*"]
        )
    )
        
    kms.Alias(
        scope,
        resource_name("key", branch),
        alias_name=resource_name("key", branch),
        target_key=cast(kms.IKey, key),
    )
    return key




