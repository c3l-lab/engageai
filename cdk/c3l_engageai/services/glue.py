from aws_cdk import (
    aws_glue,
    aws_glue_alpha,
    aws_iam,
    aws_s3,
    Fn,
    Tags
)

from aws_cdk import aws_iam, aws_kms
from constructs import Construct

from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name

def create_glue_database(scope: Construct, branch: Environment):
    # 1. Create a Glue database
    return aws_glue_alpha.Database(
            scope,
            resource_name("database", branch),
            database_name=resource_name("datalake", branch),
            description=f"Data pipeline test datalake for {branch} environment",
        )


def create_glue_crawler(
    scope: Construct, 
    branch: Environment,
    crawler_role: aws_iam.IRole, 
    glue_db: aws_glue_alpha.Database, 
    bucket_data_storage: aws_s3.IBucket
    ):
    return aws_glue.CfnCrawler(
        scope, resource_name(f"glue-crawler", branch),
        role=crawler_role.role_arn,
        database_name=glue_db.database_name,
        targets={
            "s3Targets": [
                {
                    "path": Fn.join("/", ["s3:/", bucket_data_storage.bucket_name])
                }
            ]
        },
        name=resource_name(f"glue-crawler", branch),
        # schedule=aws_glue.CfnCrawler.ScheduleProperty(
        #     # Cron runs twice daily @ 8am and 8pm
        #     schedule_expression="cron(0 1,13 * * ? *)" # Optional: twice daily at 1 AM/PM UTC
        # ),
        schema_change_policy={
            "updateBehavior": "UPDATE_IN_DATABASE",
            "deleteBehavior": "DEPRECATE_IN_DATABASE"
        }
    )