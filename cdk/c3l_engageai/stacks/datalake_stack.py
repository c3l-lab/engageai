from aws_cdk import (
    Stack,
    aws_iam,
    aws_kms,
    aws_s3
)
from constructs import Construct
from aws_cdk import aws_iam

from typing import cast
from c3l_engageai.services.iam import (
    create_glue_crawler_role,
    setup_lakeformation_access
)
from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name
from c3l_engageai.services.secretsmanager import create_secrets
from c3l_engageai.services.kms import create_datalake_kms
from c3l_engageai.services.lakeformation import (
    set_datalake_formation_initial_settings,
    set_lakeformation_administrator,
    set_data_lake_location,
    grant_database_permissions_to_execution_role,
    grant_table_permissions_to_execution_role
)
from c3l_engageai.services.s3 import (
    create_data_storage_bucket
)
from c3l_engageai.services.glue import (
    create_glue_database,
    create_glue_crawler
)
from c3l_engageai.services.datazone import (
    create_domain,
    create_environment_blueprint,
    create_project,
    create_environment_profile,
    create_environment,
    create_glue_data_source
)


class DatalakeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, branch: Environment, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # step1: create base resources
        self.key = create_datalake_kms(self, "datalake-key", branch)
        self.glue_crawler_role = create_glue_crawler_role(self, branch)
        setup_lakeformation_access(self, branch)
        set_datalake_formation_initial_settings(self, branch, self.glue_crawler_role)
        set_lakeformation_administrator(self, "lf-admin", branch, cast(aws_iam.IRole, self.glue_crawler_role))
        # role_admin_for_all_accounts = cast(
        #     aws_iam.Role,
        #     aws_iam.Role.from_role_name(self, resource_name("role-admin-for-all-accounts", branch), "AWSReservedSSO_Admin_Access_for_all_Accounts_27499b6293fca4d9")
        # )
        # role_admin = cast(
        #     aws_iam.Role,
        #     aws_iam.Role.from_role_name(self, resource_name("role-admin", branch), "AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520")
        # )

        # step2: create s3 bucket
        self.s3_data_bucket = create_data_storage_bucket(self, branch, cast(aws_kms.IKey, self.key))
        lake_formation_location = set_data_lake_location(self, branch, self.s3_data_bucket)
        self.s3_data_bucket.grant_read(self.glue_crawler_role)

        # step3: create glue resources (include database and glue crawler)
        glue_db = create_glue_database(self, branch)
        crawler = create_glue_crawler(self, branch, cast(aws_iam.IRole, self.glue_crawler_role), glue_db, self.s3_data_bucket)

        # step4: grant permission to role
        # grant_database_permissions_to_execution_role(scope=self, name=f"crawler2", branch=branch, database=glue_db, role=cast(aws_iam.Role, self.glue_crawler_role))
        # grant_database_permissions_to_execution_role(scope=self, name=f"admin-for-all", branch=branch, database=glue_db, role=cast(aws_iam.Role, role_admin_for_all_accounts))
        # grant_database_permissions_to_execution_role(scope=self, name=f"admin", branch=branch, database=glue_db, role=cast(aws_iam.Role, role_admin))

        # grant_table_permissions_to_execution_role(self, f"glue-crawler", branch, glue_db, cast(aws_iam.Role, self.glue_crawler_role))
        # grant_table_permissions_to_execution_role(self, f"admin-for-all", branch, glue_db, cast(aws_iam.Role, role_admin_for_all_accounts))
        # grant_table_permissions_to_execution_role(self, f"admin", branch, glue_db, cast(aws_iam.Role, role_admin))
        
    # def assume_role_to_sso_role(self, role: aws_iam.IRole, sso_role_name: str):
    #         # Create IAM role that can be assumed by CFN/CDK and SSO users
    #     cdk_lf_role = aws_iam.Role(
    #         self,
    #         "CDKGlueLFRole",
    #         assumed_by=cast(aws_iam.IPrincipal, aws_iam.CompositePrincipal(
    #             # CloudFormation / CDK can assume this role
    #             cast(aws_iam.IPrincipal, aws_iam.ServicePrincipal("cloudformation.amazonaws.com")),
    #             # SSO users can assume this role via SAML
    #             cast(aws_iam.IPrincipal, aws_iam.FederatedPrincipal(
    #                 f"arn:aws:iam::184898280326:saml-provider/AWSReservedSSO",
    #                 conditions={"StringEquals": {"SAML:aud": "https://signin.aws.amazon.com/saml"}}
    #             )))
    #         ),
    #         managed_policies=[
    #             aws_iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
    #         ]
    #     )