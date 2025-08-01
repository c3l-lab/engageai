from typing import Literal, Optional

from pydantic import BaseModel

Environment = Literal["anl"]


class Tag(BaseModel):
    """A key-value pair to tag AWS resources"""

    key: str
    """ The tag key """
    value: str
    """ The tag value """


class AwsAccount(BaseModel):
    """AWS Account configuration"""

    id: str
    """ The AWS Account ID """
    name: str
    """ The AWS Account name """
    region: str = "ap-southeast-2"
    """ The AWS Account region """
    env_type: str
    """ The environment type friendly name designated for the account """
    git_branch: str = "master"
    """ The git branch to use for the account """


class Config(BaseModel):
    """Configuration for the CDK deployment"""

    project_name: str
    """ The name of the project, used as a prefix for naming AWS resources """
    repository_name: str
    """ The CodeCommit git repository name """
    deployment_account: AwsAccount
    """ Where our deployment pipelines & git repos are kept """
    environment_accounts: dict[Environment, AwsAccount]
    """ The AWS Accounts for the different environments """
    default_tags: list[Tag] = []
    """ Default tags to apply to all resources """


config = Config(
    project_name="c3l-engageai",
    repository_name="c3l-engageai",
    deployment_account=AwsAccount(
        id="349398638047",
        name="C3L-CODE",
        env_type="c3l-code",
    ),
    environment_accounts={
        "anl": AwsAccount(
            id="184898280326",
            name="C3L-ANALYTICS",
            env_type="development",
            git_branch="master",
        ),
    },
    default_tags=[
        Tag(key="Project", value="c3l-engageai"),
        Tag(key="PrimaryContact", value="C3L"),
    ],
)
