import aws_cdk
import os
# from aws_cdk import Duration, Environment, Stage
from constructs import Construct

from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name

from c3l_engageai.stacks.secrets import Secrets
from c3l_engageai.stacks.datazone_stack import DataZoneStack
from c3l_engageai.stacks.datalake_stack import DatalakeStack

class DeployStage(aws_cdk.Stage):
    def __init__(
        self, scope: Construct, id: str, branch: Environment,**kwargs
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
        
        construct_id = resource_name("datazone", branch)
        datazone_stack= DataZoneStack(
            self,
            construct_id=construct_id,
            branch=branch,
            env=env
        )
        datazone_stack.add_dependency(secrets_stack)

        construct_id = resource_name("datalake", branch)
        datalake_stack= DatalakeStack(
            self,
            construct_id=construct_id,
            branch=branch,
            env=env
        )
        datalake_stack.add_dependency(secrets_stack)

        

