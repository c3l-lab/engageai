
export PATH := $(PATH)

# Check if a .env file exists, and then load it
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

install:
	poetry install

synth: install
	npx cdk synth

lint: export PYRIGHT_PYTHON_FORCE_VERSION = latest
lint: install
	poetry run pyright

test: install
	poetry run pytest

format: install
	poetry run ruff format

# Deploy all our pipelines (necessary to do once manually to get the self-mutating CDK pipeline up and running)
deploy: synth
	npx cdk deploy --verbose --all ${DEPLOYMENT_AWS_PROFILE}

# This bootstraps the CDK environment in the target accounts and gives the pipelines their required permissions. Only needs to be run once.
bootstrap:
	poetry run python bootstrap.py

# Upload the secrets in the 'secrets/' directory to AWS Secrets Manager
secrets-upload:
	poetry run python secrets.py upload

# Fetches the secrets from AWS Secrets Manager and puts them in the 'secrets/' directory
secrets-download:
	poetry run python secrets.py download

.PHONY: install synth lint test deploy bootstrap secrets-upload secrets-download format all sagemaker

all: install