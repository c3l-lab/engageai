import os
import subprocess

from c3l_engageai.config import config

""" 
For more information on bootstrapping see: https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html
Make sure you have setup your .env file with the AWS profiles for the deployment and environment accounts.
"""

# These are the permissions the pipelines will have when deploying across accounts
access_policy = """--cloudformation-execution-policies 'arn:aws:iam::aws:policy/AdministratorAccess'"""

# Bootstrap the deployment account
aws_profile = os.environ["DEPLOYMENT_AWS_PROFILE"]
subprocess.run(
    f"npx cdk bootstrap {config.deployment_account.id}/{config.deployment_account.region} {aws_profile} {access_policy}",
    shell=True,
)

# Bootstrap the environment accounts, allowing the deployment account to deploy to them
for branch, account in config.environment_accounts.items():
    aws_profile = os.environ.get(f"{branch.upper()}_AWS_PROFILE")
    if not aws_profile:
        print(
            f"Skipping bootstrapping for the '{branch}' account. Set {branch.upper()}_AWS_PROFILE in your .env file."
        )
        continue
    subprocess.run(
        f"npx cdk bootstrap {account.id}/{account.region} --trust {config.deployment_account.id} {aws_profile} {access_policy}",
        shell=True,
    )
