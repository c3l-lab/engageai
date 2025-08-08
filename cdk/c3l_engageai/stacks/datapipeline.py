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

        # 1. Execution Role
        execution_role = create_datazone_execution_role(
            self, branch, self.stack_name
        )

        bucket = aws_s3.Bucket.from_bucket_name(
            self, "EngageAiDatasetBucket",
            bucket_name="engage-ai-dataset",
        )
        
        # 2. Domain
        domain, project = create_datazone(
            self, 
            execution_role,
            s3_bucket=bucket,
            s3_prefix_key="engageai_indicator/"
        )


