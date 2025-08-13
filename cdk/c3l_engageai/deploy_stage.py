import aws_cdk
import os
# from aws_cdk import Duration, Environment, Stage
from constructs import Construct

from c3l_engageai.config import Environment, config 
from c3l_engageai.helpers import resource_name

from c3l_engageai.stacks.secrets import Secrets
from c3l_engageai.stacks.datapipeline import Datapipeline
from c3l_engageai.stacks.datazone_cdk_stack import DataZoneFullStack

class DeployStage(aws_cdk.Stage):
    def __init__(
        self, scope: Construct, id: str, branch: Environment, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Deploy the stacks to the correct AWS account
        env = aws_cdk.Environment(
            account=config.environment_accounts[branch].id,
            region=config.environment_accounts[branch].region,
        )
        
        # This stack holds all our SecretsManager secrets.
        # It's a good idea for it to be separate from the other stacks, since it must
        # have it's resources created before any other stack uses its secrets.
        secrets_stack_name = resource_name("secrets-stack", branch)
        secrets_stack = Secrets(
            self,
            secrets_stack_name,
            branch=branch,
            stack_name=secrets_stack_name,
            env=env,
        )

        datapipeline_stack = Datapipeline(
            self, 
            resource_name("datapipeline-stack", branch), 
            branch=branch, 
            env=env)
        datapipeline_stack.add_dependency(secrets_stack)


        datazonefullstack= DataZoneFullStack(
            self,
            "DataZoneFullStack",
            domain_execution_role_ar = self.domain_execution_role_arn, 
            # domain_execution_role_arn=os.getenv("DOMAIN_EXECUTION_ROLE_ARN", "arn:aws:iam::123456789012:role/MyDataZoneDomainExecutionRole"),
            domain_kms_key_arn=os.getenv("DOMAIN_KMS_KEY_ARN", "arn:aws:kms:ap-southeast-2:123456789012:key/11111111-2222-3333-4444-555555555555"),
            dz_provisioning_role_arn=os.getenv("DZ_PROVISIONING_ROLE_ARN", "arn:aws:iam::123456789012:role/MyDzProvisioningRole"),
            glue_manage_access_role_arn=os.getenv("GLUE_MANAGE_ACCESS_ROLE_ARN", "arn:aws:iam::123456789012:role/MyGlueManageAccessRole"),
            s3_bucket_for_data_lake=os.getenv("S3_BUCKET_FOR_DATA_LAKE", "my-datalake-bucket"),
            domain_name=os.getenv("DOMAIN_NAME", "MyDataZoneDomain"),
            env={
                "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
                "region": os.getenv("CDK_DEFAULT_REGION", "ap-southeast-2"),
            },
        )




#     DataZoneDomainStack(
#     scope=app,
#     id="DataZoneDomainStack",
#     domain_execution_role_arn=DOMAIN_EXECUTION_ROLE_ARN,
#     domain_kms_key_arn=DOMAIN_KMS_KEY_ARN,
#     domain_name=DOMAIN_NAME,
#     env=cdk.Environment(
#         account=os.getenv("CDK_DEFAULT_ACCOUNT"),
#         region=os.getenv("CDK_DEFAULT_REGION", "ap-southeast-2")
#     )
# )


