from aws_cdk import Stack
from constructs import Construct

from c3l_engageai.config import Environment
from c3l_engageai.services.secretsmanager import create_secrets


class Secrets(Stack):
    """
    We are creating a stack that will only contain SecretsManager secrets.
    This stack needs to be deployed before any other stack that uses secrets.
    """

    def __init__(
        self, scope: Construct, construct_id: str, branch: Environment, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        create_secrets(self, branch)
