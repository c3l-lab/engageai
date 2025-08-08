#!/usr/bin/env python3

import aws_cdk as cdk

from c3l_engageai.config import config
from c3l_engageai.pipeline import Pipeline
from c3l_engageai.stacks.datazone_cdk_stack import DatazoneCdkStack

app = cdk.App()

deployment_environment = cdk.Environment(
    account=config.deployment_account.id, region=config.deployment_account.region
)

Pipeline(
    app,
    f"{config.project_name}-pipeline-anl",
    "anl",
    env=deployment_environment,
)


DatazoneCdkStack(
    app, 
    f"{config.project_name}-pipeline-DatazoneCdkStac",
    "DatazoneCdkStack",
    env=deployment_environment,
    )
app.synth()


