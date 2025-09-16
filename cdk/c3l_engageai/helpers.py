import os

from aws_cdk import aws_certificatemanager
from constructs import Construct

from c3l_engageai.config import Environment, config


def resolve_secret(secret_name: str, branch: Environment) -> str:
    """Resolve a secret from AWS Secrets Manager in the target environment AWS account"""
    return f"{{{{resolve:secretsmanager:{resource_name('secrets', branch)}:SecretString:{secret_name}}}}}"


def resource_name(name: str, branch: Environment) -> str:
    """Helper function to consistently name resources"""
    return f"{config.project_name}-{name}-{branch}"


def resolve_module_path(path: str) -> str:
    """Resolve the path to the modules directory `/modules'
    So a path like `modules/mas_shared/pyproject.toml` can be accesed like `resolve_module_path('mas_shared/pyproject.toml')`
    """
    return os.path.join(os.path.dirname(__file__), "../..", "modules", path)


def get_certificate(
    scope: Construct, branch: Environment
) -> aws_certificatemanager.ICertificate:
    """
    Get the wildcard Matter and Space certificate for the given branch
    """
    return aws_certificatemanager.Certificate.from_certificate_arn(
        scope,
        id=resource_name("certificate", branch),
        certificate_arn=resolve_secret("CERTIFICATE_ARN", branch),
    )
