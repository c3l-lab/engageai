import os
from typing import Dict, List, cast, Any
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

def create_shared_lambda_layer(
        scope: Construct,
        entry_path: str = "../modules/",
    ) -> aws_lambda.ILayerVersion:
    lambda_name: str = "lambdas"
    lambda_layer_name = f"{lambda_name}_layer"
    # Create Lambda Layer from Poetry dependencies
    layer_version = aws_lambda.LayerVersion(scope, lambda_layer_name,
        code=aws_lambda.Code.from_asset(entry_path,
            bundling={
                "image": aws_lambda.Runtime.PYTHON_3_11.bundling_image,
                "command": [
                    "bash", "-c",
                    f"""
                    pip install --no-cache-dir poetry && \
                    pip install poetry-plugin-export && \
                    poetry --version && \
                    pwd && \
                    ls ./ && \
                    mkdir -p /asset-output/python && \
                    cd lambdas && \
                    poetry export --only dev -f requirements.txt --without-hashes --only main > /asset-output/requirements.txt && \
                    cd /asset-output && \
                    pip install -r requirements.txt -t /asset-output/python
                    # """
                ],
                "user": "root"
            }
        ),
        compatible_architectures=[aws_lambda.Architecture.X86_64],
        compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
        description=f"Lambda {lambda_name} Layer with Poetry dependencies",
        layer_version_name=lambda_layer_name
    )
    return cast(aws_lambda.ILayerVersion, layer_version)


def create_lambda_athena_query(
    scope: Construct,
    branch: Environment,
    role: aws_iam.IRole,
    **kwargs: Dict[str, Any]
) -> aws_lambda.IFunction:
    lambda_layers = []
    if kwargs.__contains__("lambda_layer"):
        lambda_layers = kwargs["lambda_layer"]
    lambda_folder = "athena_query"   # The lambda folder located in the lambdas directory
    handler_file = f"{lambda_folder}/index.py" # The lambda handler file (lambda handler function need to be located in the file)
    lambda_name = resource_name("lambda-athena-query", branch)
    lambda_function = lambda_python.PythonFunction(
        scope, 
        lambda_name,
        function_name=lambda_name,
        entry="../modules/",  # Directory containing your lambda code and pyproject.toml
        index=f"lambdas/{handler_file}",  # Your lambda handler file
        handler="lambda_handler",  # Function name in main.py
        runtime=aws_lambda.Runtime.PYTHON_3_11,
        timeout=Duration.seconds(300),
        memory_size=512,
        role=role,
        tracing=aws_lambda.Tracing.ACTIVE,
        bundling=lambda_python.BundlingOptions(
            command=[
                "bash", "-c",
                f"""
                export HOME="/tmp" && \
                pip install --no-cache-dir poetry && \
                poetry config virtualenvs.create true --local && \
                cd lambdas/{lambda_folder} && mkdir /asset-output/{lambda_folder} && \
                find . -type f -name "*.py" -exec cp --parents {"{}"} /asset-output/{lambda_folder}/ \; && \
                echo "before install package" && \
                ls /asset-output && \
                poetry export -f requirements.txt --without-hashes --without dev --only main > /asset-output/requirements.txt &&\
                cd /asset-output && \
                pip install -r requirements.txt -t . && \
                echo requirements.txt && \
                echo "after install" && \
                ls -lh .
                """
            ]
        ),
        layers=lambda_layers,
    )
    # Explicitly cast to IFunction
    base_function = cast(aws_lambda.IFunction, lambda_function)
    return base_function
