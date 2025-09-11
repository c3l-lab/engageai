import json

from aws_cdk import (
    aws_lakeformation, 
    Stack, 
    aws_s3, 
    aws_iam,
    aws_glue_alpha
)
from constructs import Construct
from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name


def set_datalake_formation_initial_settings(
    scope: Construct, branch: Environment, role: aws_iam.Role
) -> aws_lakeformation.CfnDataLakeSettings:
    settings = aws_lakeformation.CfnDataLakeSettings(
        scope=scope,
        id="LakeFormationAdminPermissionsCDKCFN",
        admins=[
            aws_lakeformation.CfnDataLakeSettings.DataLakePrincipalProperty(
                data_lake_principal_identifier=role.role_arn
                # data_lake_principal_identifier=resolve_secret(
                #     "CDK_CFN_EXECUTION_ROLE_ARN", branch
                # )
            )
        ],
    )
    return settings 

def set_lakeformation_administrator(scope: Construct, name: str, branch: Environment, role: aws_iam.IRole):
    # Grant this role admin privileges in Lake Formation
    aws_lakeformation.CfnDataLakeSettings(
        scope, 
        resource_name(name, branch),
        admins=[{
            "dataLakePrincipalIdentifier": role.role_arn
        }]
    )

def set_data_lake_location(
    scope: Construct, branch: Environment, s3_bucket: aws_s3.Bucket
) -> aws_lakeformation.CfnResource:
    account_id = config.environment_accounts[branch].id
    location = aws_lakeformation.CfnResource(
        scope=scope,
        id=f"{branch}-LakeFormationDataLakeLocation",
        hybrid_access_enabled=True,
        resource_arn=s3_bucket.bucket_arn,
        use_service_linked_role=True,
        role_arn=f"arn:aws:iam::{account_id}:role/aws-service-role/lakeformation.amazonaws.com/AWSServiceRoleForLakeFormationDataAccess",
    )
    return location

def grant_database_permissions_to_execution_role(
    scope: Construct,
    name: str,
    branch: Environment,
    database: aws_glue_alpha.Database,
    role: aws_iam.Role,
) -> aws_lakeformation.CfnPrincipalPermissions:
    permission = aws_lakeformation.CfnPrincipalPermissions(
        scope=scope,
        id=resource_name(f"{name}-db-permissions", branch),
        permissions=["ALL"],
        permissions_with_grant_option=["ALL"],
        principal=aws_lakeformation.CfnPrincipalPermissions.DataLakePrincipalProperty(
            data_lake_principal_identifier=role.role_arn
        ),
        resource=aws_lakeformation.CfnPrincipalPermissions.ResourceProperty(
            database=aws_lakeformation.CfnPrincipalPermissions.DatabaseResourceProperty(
                catalog_id=database.catalog_id, name=database.database_name
            )
        ),
    )

    return permission

def grant_table_permissions_to_execution_role(
    scope: Construct,
    name: str,
    branch: Environment,
    database: aws_glue_alpha.Database,
    role: aws_iam.Role,
) -> aws_lakeformation.CfnPrincipalPermissions:
    permission = aws_lakeformation.CfnPrincipalPermissions(
        scope=scope,
        id=resource_name(f"{name}-tbl-permission", branch),
        permissions=["ALL"] , #["SELECT", "INSERT", "DELETE", "ALTER", "DROP", "DESCRIBE"],
        permissions_with_grant_option=[
            "ALL"
            # "SELECT",
            # "INSERT",
            # "DELETE",
            # "ALTER",
            # "DROP",
            # "DESCRIBE",
        ],
        principal=aws_lakeformation.CfnPrincipalPermissions.DataLakePrincipalProperty(
            data_lake_principal_identifier=role.role_arn
        ),
        resource=aws_lakeformation.CfnPrincipalPermissions.ResourceProperty(
            table=aws_lakeformation.CfnPrincipalPermissions.TableResourceProperty(
                catalog_id=database.catalog_id,
                database_name=database.database_name,
                table_wildcard=json.loads("{}"),
            )
        ),
    )

    return permission