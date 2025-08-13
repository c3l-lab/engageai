from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_iam as iam

from c3l_engageai.services.iam import create_datazone_execution_role
from c3l_engageai.config import Environment
from c3l_engageai.services.secretsmanager import create_secrets
from c3l_engageai.services.datazone import (
    create_domain,
    create_project,
    create_environment_profile,
    create_environment,
    create_s3_data_source
)


class DataZoneFullStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # execution_role = iam.Role(
        #     self, "DataZoneExecutionRole",
        #     assumed_by=iam.ServicePrincipal("datazone.amazonaws.com"),
        #     managed_policies=[
        #         iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
        #         iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
        #     ]
        # )

        execution_role= create_datazone_execution_role (self, )

        # AWS Account and region (use your actual values or context)
        account_id = self.account
        region = self.region

        # Call the service functions in order
        domain = create_domain(self, execution_role)
        project = create_project(self, domain)
        env_profile = create_environment_profile(self, domain, project, account_id, region)
        environment = create_environment(self, domain, project, env_profile)
        data_source = create_s3_data_source(self, domain, environment)

        # (Optional) expose as attributes if you want to reference them later
        self.domain = domain
        self.project = project
        self.environment_profile = env_profile
        self.environment = environment
        self.data_source = data_source
