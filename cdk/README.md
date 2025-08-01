# Matter and Space MLOps CDK project

This is an AWS CDK project that deploys the Matter and Space Platform.

It uses the later style of [self-mutating pipelines](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html) to deploy the CDK stacks.

## Configuration

See the `mas_mlops/config.py` directory for the configuration files.

## Secrets and AWS Secrets Manager

The particularly interesting behaviour of this CDK setup is how it manages secrets within AWS Secrets Manager.

Our problem is we have many different "secrets" that need to be managed across all 3 environments (dev, stage, prod).
These may be different in each environment and it's annoying manually managing these in the AWS Secrets Manager console.

Instead, we have a `secrets/` directory in this repository that contains JSON files with the secrets in them, and then provide scripts to update
AWS Secrets Manager in each AWS account with these secrets.

1. The CDK pipeline will deploy an empty secret to each AWS environment.
1. From here, you can run `make secrets-upload` to upload local secrets to AWS Secrets Manager for each environment.
   - See the `secrets/` directory for examples of the secrets JSON files.
     - `secrets/dsh.json` will be uploaded to AWS Secrets Manager in the Data Science Hub environment.
2. You can run `make secrets-download` which will download all the secrets from AWS Secrets Manager to the `secrets/` directory.

You'll need to make sure your `.env` file is set up correctly to do this. Any environments that are commented out in the `.env` file will not be uploaded/downloaded.
