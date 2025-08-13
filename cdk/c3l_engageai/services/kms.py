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
from c3l_engageai.config import Environment

def create_datazone_kms(scope: Construct, construct_id: str, branch: Environment) -> kms.Key:
    # Create KMS key for encryption
    return  kms.Key(
        scope, construct_id,
        kms__name=resource_name("datazone_kms", branch),
        description="KMS key for DataZone encryption",
        enable_key_rotation=True,
        removal_policy=RemovalPolicy.DESTROY
    )

