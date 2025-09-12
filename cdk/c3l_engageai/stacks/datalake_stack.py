from aws_cdk import (
    Stack,
    aws_iam,
    aws_kms,
    aws_s3,
    aws_glue_alpha
)
from constructs import Construct
from aws_cdk import aws_iam

from typing import cast
from c3l_engageai.services.iam import (
    create_glue_crawler_role,
    setup_lakeformation_access,
    create_datazone_execution_role
)
from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name
from c3l_engageai.services.secretsmanager import create_secrets
from c3l_engageai.services.kms import (
    create_datalake_kms,
    create_datazone_kms
)
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

        # 2. Grant KMS key usage (Decrypt, Encrypt, GenerateDataKey)
        self.grant_key_permission_to_role(
            cast(aws_kms.IKey, self.key), 
            cast(aws_iam.IRole, self.glue_crawler_role)
        )

        setup_lakeformation_access(self, branch)
        set_datalake_formation_initial_settings(self, branch, self.glue_crawler_role)
        set_lakeformation_administrator(self, "lf-admin", branch, cast(aws_iam.IRole, self.glue_crawler_role))
        
        # step2: create s3 bucket
        self.s3_data_bucket = create_data_storage_bucket(self, branch, cast(aws_kms.IKey, self.key))
        lake_formation_location = set_data_lake_location(self, branch, self.s3_data_bucket)
        self.s3_data_bucket.grant_read(self.glue_crawler_role)

        # step3: create glue resources (include database and glue crawler)
        glue_db = create_glue_database(self, branch)
        crawler = create_glue_crawler(self, branch, cast(aws_iam.IRole, self.glue_crawler_role), glue_db, self.s3_data_bucket)

        # step4: grant permission to role
        self.grant_database_permissions(branch, glue_db, cast(aws_iam.IRole, self.glue_crawler_role))

    def grant_key_permission_to_role(self, key: aws_kms.IKey, role: aws_iam.IRole):
        # Grant KMS key usage (Decrypt, Encrypt, GenerateDataKey)
        key.grant_encrypt_decrypt(role)
        key.grant(role, "kms:GenerateDataKey*")

    def grant_database_permissions(self, branch: Environment, glue_db: aws_glue_alpha.Database, crawler_role: aws_iam.IRole):
        # role_admin_for_all_accounts = cast(
        #     aws_iam.Role,
        #     aws_iam.Role.from_role_arn(
        #         self, 
        #         resource_name("role-admin-for-all-accounts", branch), 
        #         "arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_Admin_Access_for_all_Accounts_27499b6293fca4d9"
        #     )
        # )
        role_admin = cast(
            aws_iam.Role,
            aws_iam.Role.from_role_arn(
                self, 
                resource_name("role-admin", branch), 
                "arn:aws:iam::184898280326:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_AWSAdministratorAccess_e0be9866f0d62520"
            )
        )
        grant_database_permissions_to_execution_role(scope=self, name=f"crawler", branch=branch, database=glue_db, role=cast(aws_iam.Role, crawler_role))
        grant_table_permissions_to_execution_role(self, f"crawler", branch, glue_db, cast(aws_iam.Role, crawler_role))
        # grant_database_permissions_to_execution_role(scope=self, name=f"admin-all", branch=branch, database=glue_db, role=role_admin_for_all_accounts)
        # grant_table_permissions_to_execution_role(self, f"admin-all", branch, glue_db, cast(aws_iam.Role, role_admin_for_all_accounts))
        grant_database_permissions_to_execution_role(scope=self, name=f"admin", branch=branch, database=glue_db, role=cast(aws_iam.Role, role_admin))
        grant_table_permissions_to_execution_role(self, f"admin", branch, glue_db, cast(aws_iam.Role, role_admin))

        self.create_datazone(branch)

    def create_datazone(self, branch: Environment):
        # datazone_kms = create_datazone_kms(self, resource_name("datazone-kms", branch), branch)
        datazone_kms = self.key
        execution_role= create_datazone_execution_role (self, resource_name("datazone_execution_role", branch), branch)       
        self.grant_key_permission_to_role(
            cast(aws_kms.IKey, self.key), 
            cast(aws_iam.IRole, execution_role)
        )
        # Call the service functions in order
        domain_id = create_domain(self, branch,  execution_role, cast(aws_kms.IKey, datazone_kms))

        blueprint_id = create_environment_blueprint(self, domain_id, execution_role)
        # =================================================
        # Please modify the following code according to the code above
        
        project_id = create_project(self, domain_id)
        env_profile_id = create_environment_profile(
            self, domain_id, project_id, blueprint_id, branch
        )
        environment_id = create_environment(
            self, domain_id, project_id, env_profile_id, branch, execution_role
        )