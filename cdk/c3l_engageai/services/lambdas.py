import os
from typing import Dict, List, cast
from aws_cdk import (
    Duration,
    aws_iam,
    aws_s3,
    aws_lambda,
    aws_lambda_python_alpha as lambda_python,
    Size,
)
from constructs import Construct
import subprocess

from c3l_engageai.config import Environment, config
from c3l_engageai.helpers import resource_name, resolve_secret

def create_lambda_athena_query(
    scope: Construct,
    branch: Environment,
    role: aws_iam.IRole,
) -> aws_lambda.IFunction:

    lambda_name = resource_name("lambda-athena-query", branch)
    lambda_function = lambda_python.PythonFunction(
        scope, 
        lambda_name,
        function_name=lambda_name,
        entry="../modules/",  # Directory containing your lambda code and pyproject.toml
        index="athena_query/index.py",  # Your lambda handler file
        handler="lambda_handler",  # Function name in main.py
        runtime=aws_lambda.Runtime.PYTHON_3_11,
        timeout=Duration.seconds(300),
        memory_size=512,
        role=role,
        tracing=aws_lambda.Tracing.ACTIVE,
        bundling=lambda_python.BundlingOptions(
            command=[
                "bash", "-c",
                """
                export HOME="/tmp" && \
                pip install --no-cache-dir poetry && \
                poetry config virtualenvs.create true --local && \
                cd athena_query && mkdir /asset-output/athena_query && \
                find . -type f -name "*.py" -exec cp --parents {} /asset-output/athena_query/ \; && \
                echo "before install package" && \
                ls /asset-output && \
                pwd && \
                ls . && \
                cd athena_query/ && \
                poetry export -f requirements.txt --without-hashes --only main > /asset-output/requirements.txt &&\
                cd /asset-output && \
                pip install -r requirements.txt -t . && \
                echo requirements.txt && \
                echo "after install" && \
                ls -lh .
                """
            ]
            # Use poetry to install dependencies
            #command=[
            #    "bash", "-c",
            #    """
            #    export HOME="/tmp" && \
            #    pip install --no-cache-dir poetry && \
            #    poetry config virtualenvs.create false --local && \
            #    find . -type f -name "*.py" -exec cp --parents {} /asset-output/ \; && \
            #    cp pyproject.toml poetry.lock /asset-output/ 2>/dev/null || true && \
            #    poetry export -f requirements.txt --without-hashes --only main > /asset-output/requirements.txt && \
            #    cd /asset-output && \
            #    pip install -r requirements.txt -t .
            #    """
            #]
        )
    )
    
    # Explicitly cast to IFunction
    base_function = cast(aws_lambda.IFunction, lambda_function)
    return base_function
