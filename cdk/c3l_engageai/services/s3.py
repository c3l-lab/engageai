#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_datazone as datazone,
    aws_s3 as s3,
    aws_s3,
    aws_iam as iam,
    aws_kms as kms,
    RemovalPolicy,
    Duration
)
from constructs import Construct
import json
from typing import cast
from c3l_engageai.config import Environment
from c3l_engageai.helpers import resource_name

def create_data_storage_bucket(
        scope: Construct, 
        branch: Environment, 
        # name: str, 
        kms_key: kms.IKey
    ):
    return aws_s3.Bucket(
        scope,
        resource_name(f"data-storage", branch),
        bucket_name=resource_name(f"data-storage", branch),
        block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
        removal_policy=RemovalPolicy.DESTROY,
        auto_delete_objects=branch != "prod",
        object_ownership=aws_s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        versioned=True,
        encryption=aws_s3.BucketEncryption.KMS,
        encryption_key=kms_key
    )

def create_datazone_s3_bucket(scope: Construct, datazone_kms_key: kms.Key) -> s3.Bucket:
    return s3.Bucket(
        scope, "DataZoneDataBucket",
        bucket_name=f"datazone-data-bucket-test",
        versioned=True,
        encryption=s3.BucketEncryption.KMS,
        encryption_key=cast(kms.IKey, datazone_kms_key),
        block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        removal_policy=RemovalPolicy.DESTROY,
        auto_delete_objects=True,
        lifecycle_rules=[
            s3.LifecycleRule(
                id="DataLifecycleRule",
                enabled=True,
                transitions=[
                    s3.Transition(
                        storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                        transition_after=Duration.days(30)
                    ),
                    s3.Transition(
                        storage_class=s3.StorageClass.GLACIER,
                        transition_after=Duration.days(90)
                    )
                ]
            )
        ]
    )
