from aws_cdk import RemovalPolicy, aws_secretsmanager
from constructs import Construct

from c3l_engageai.config import Environment
from c3l_engageai.helpers import resource_name


def create_secrets(scope: Construct, branch: Environment):
    """The secret values themselves are not set here.
    This just creates the secret object in the CDK stack
    """
    name = resource_name("secrets", branch)
    return aws_secretsmanager.Secret(
        scope,
        name,
        secret_name=name,
        removal_policy=RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
        secret_object_value={},
    )
