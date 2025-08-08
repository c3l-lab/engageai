from aws_cdk import (
    Stack,
    aws_s3
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
from c3l_engageai.services.s3 import (
    create_datazone_s3_bucket
)
from c3l_engageai.services.kms import (
    create_datazone_kms
)
from c3l_engageai.config import config
class Datapipeline(Stack):
    """
    We are creating a stack that will only contain SecretsManager secrets.
    This stack needs to be deployed before any other stack that uses secrets.
    """

    def __init__(
        self, scope: Construct, construct_id: str, branch: Environment, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_execute_role = create_lambda_default_execution_role(
            self, branch, construct_id
        )
        lambda_layer = create_shared_lambda_layer(self)
        create_lambda_athena_query(
            self,
            branch=branch,
            role=lambda_execute_role,
            lambda_layer=[lambda_layer]
        )

        kms = create_datazone_kms(self, "datazone-kms-key")
        bucket = create_datazone_s3_bucket(self, kms)

        
        # 1. Execution Role
        execution_role = create_datazone_execution_role(
            self, kms, bucket
        )
        # 2. Domain
        domain, project = create_datazone(
            self, 
            execution_role,
            s3_bucket=bucket,
            s3_prefix_key="engageai_indicator/",
            account = config.environment_accounts[branch].id,
            region = config.environment_accounts[branch].region
        )


