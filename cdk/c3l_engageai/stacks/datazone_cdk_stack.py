from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_iam as iam

from c3l_engageai.services.iam import create_datazone_execution_role
from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name
from c3l_engageai.services.secretsmanager import create_secrets
from c3l_engageai.services.kms import create_datazone_kms
from c3l_engageai.services.datazone import (
    create_domain,
    create_project,
    create_environment_profile,
    create_environment,
    create_s3_data_source
)


class DataZoneFullStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, branch: Environment, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        datazone_kms = create_datazone_kms(self, resource_name("datazone_kms", branch), branch)
        execution_role= create_datazone_execution_role (self, resource_name("datazone_execution_role", branch), branch)       
        # Call the service functions in order
        domain_id = create_domain(self, execution_role, datazone_kms)


        # =================================================
        # Please modify the following code according to the code above
        
        project_id = create_project(self, domain_id)
        env_profile_id = create_environment_profile(
            self, domain_id, project_id
        )

        environment_id = create_environment(
            self, domain_id, project_id, env_profile_id
        )
        data_source_id = create_s3_data_source(
            self, domain_id, environment_id, project_id
        )

        