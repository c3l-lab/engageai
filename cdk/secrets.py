# pyright: ignore-file

import json
import os
import subprocess
import sys

from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name

""" 
This script provides a way to upload / download the secrets for each environment from AWS Secrets Manager.

Maintain a `./secrets` directory with the secrets for each environment, and keep an `example.json` file for reference.

Run as `python secrets.py upload` or `python secrets.py download`, or use the Makefile convenience commands.
"""

if len(sys.argv) != 2:
    raise ValueError("Please provide an action: 'upload' or 'download'")

def download(
    branch: Environment, aws_profile: str, secrets_json_file: str, name="secrets"
):
    result = subprocess.run(
        f"aws secretsmanager get-secret-value --secret-id {resource_name(name, branch)} --query SecretString --output json {aws_profile} --region {config.environment_accounts[branch].region}",
        check=True,
        shell=True,
        capture_output=True,
    )
    secrets = json.loads(json.loads(result.stdout.decode()))
    with open(secrets_json_file, "w") as f:
        json.dump(secrets, f, indent=2)
    print(f"Downloaded {branch} {name} to {secrets_json_file}")


def upload(
    branch: Environment, aws_profile: str, secrets_json_file: str, name="secrets"
):
    if not os.path.exists(secrets_json_file):
        raise FileNotFoundError(f"Secrets file not found: {secrets_json_file}")
    with open(secrets_json_file, "r") as f:
        secrets = json.load(f)
    subprocess.run(
        f"aws secretsmanager put-secret-value --secret-id {resource_name(name, branch)} --secret-string '{json.dumps(secrets)}' {aws_profile} --region {config.environment_accounts[branch].region}",
        check=True,
        shell=True,
        capture_output=True,
    )
    print(f"Uploaded {branch} {name} to AWS Secrets Manager")


if sys.argv[1] == "download":
    # Download the secrets for each environment
    for branch, _ in config.environment_accounts.items():
        aws_profile = os.environ.get(f"{branch.upper()}_AWS_PROFILE")
        if not aws_profile:
            print(
                f"Skipping '{branch}', {branch.upper()}_AWS_PROFILE is not set in .env"
            )
            continue
        secrets_json_file = f"./secrets/{branch}.json"
        if os.path.exists(secrets_json_file):
            if input(f"Overwrite {secrets_json_file}? (y/n): ").lower() != "y":
                continue
        download(branch, aws_profile, secrets_json_file)

elif sys.argv[1] == "upload":
    # Upload the secrets for each environment
    for branch, account in config.environment_accounts.items():
        aws_profile = os.environ.get(f"{branch.upper()}_AWS_PROFILE")
        if not aws_profile:
            print(
                f"Skipping '{branch}', {branch.upper()}_AWS_PROFILE is not set in .env"
            )
            continue
        secrets_json_file = f"./secrets/{branch}.json"
        upload(branch, aws_profile, secrets_json_file)
