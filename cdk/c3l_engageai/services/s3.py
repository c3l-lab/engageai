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

def create_datazone_s3_bucket(scope: Construct, stack: Stack) -> s3.Bucket:
    return s3.Bucket(
        self, "DataZoneDataBucket",
        bucket_name=f"datazone-data-bucket-{self.account}-{self.region}",
        versioned=True,
        encryption=s3.BucketEncryption.KMS,
        encryption_key=datazone_kms_key,
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
