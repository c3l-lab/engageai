from typing import List, cast
from aws_cdk import (
    Duration, aws_apigateway, aws_lambda, 
    aws_iam, 
    aws_apigatewayv2_authorizers, 
    aws_apigatewayv2 as apigw_v2, 
    aws_apigatewayv2_integrations as apigw_integrations
)
from constructs import Construct

from c3l_engageai.config import Environment
from c3l_engageai.helpers import get_certificate, resource_name


def create_agent_orchestration_api_gateway(
    scope: Construct,
    branch: Environment,
    lambda_function: aws_lambda.IFunction,
) -> aws_apigateway.RestApi:
    ###################################################################
    ## First Approach 
    # agent_orchestration_api = aws_apigateway.RestApi(
    #     scope,
    #     "AgentOrchestrationOpsApi",
    #     rest_api_name=resource_name("api", branch),
    #     domain_name={
    #         #"domain_name": f"{resource_name('api', branch)}.c3l.ai",
    #         "domain_name": f"agent.c3l.ai",
    #         "certificate": get_certificate(scope, branch),
    #     },
    #     default_cors_preflight_options=aws_apigateway.CorsOptions(
    #         allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
    #         allow_methods=aws_apigateway.Cors.ALL_METHODS,
    #         allow_headers=[
    #             "Content-Type",
    #             "Authorization",
    #             "X-Amz-Date",
    #             "X-Api-Key",
    #             "X-Amz-Security-Token",
    #             "authtoken",
    #         ],
    #     ),
    #     deploy_options=aws_apigateway.StageOptions(
    #         stage_name="api", tracing_enabled=True
    #     ),
    #     endpoint_configuration=aws_apigateway.EndpointConfiguration(
    #         types=[aws_apigateway.EndpointType.REGIONAL]
    #     ),
    # )
    # agent_orchestration_api_key = agent_orchestration_api.add_api_key(
    #     "AgentOrchestrationApiKey",
    #     description="API Key for the Agent Orchestration API",
    #     api_key_name=resource_name("api-key", branch),
    # )
    # agent_orchestration_api_usage_plan = agent_orchestration_api.add_usage_plan(
    #     "AgentOrchestrationApiUsagePlan",
    #     name=resource_name("api-usage-plan", branch),
    #     throttle=aws_apigateway.ThrottleSettings(burst_limit=1000, rate_limit=2000),
    # )
    # agent_orchestration_api_usage_plan.add_api_key(agent_orchestration_api_key)
    # agent_orchestration_api_usage_plan.add_api_stage(
    #     stage=agent_orchestration_api.deployment_stage
    # )
    # agent_orchestration_api_proxy_resource = agent_orchestration_api.root.add_resource("{proxy+}")
    # agent_orchestration_api_proxy_integration = aws_apigateway.LambdaIntegration(
    #     lambda_function,
    #     proxy=True,
    #     timeout=Duration.seconds(29),
    # )
    # for method in ["GET", "PUT", "POST", "DELETE"]:
    #     agent_orchestration_api_proxy_resource.add_method(
    #         method,
    #         agent_orchestration_api_proxy_integration,
    #         request_parameters={"method.request.path.proxy": True},
    #         #api_key_required=True,
    #         api_key_required=False,
    #     )
    # return agent_orchestration_api

    ###################################################################
    ## Second Approach 
    # Create HTTP API
    http_api = apigw_v2.HttpApi(
        scope, "ChainlitHttpApi",
        description="API Gateway HTTP API for Chainlit"
    )
    
    # Add Lambda integration
    lambda_integration = apigw_integrations.HttpLambdaIntegration(
        "ChainlitLambdaIntegration", handler=lambda_function
    )
    
    # Add routes to the HTTP API
    http_api.add_routes(
        path="/{proxy+}",
        methods=[apigw_v2.HttpMethod.ANY],
        integration=lambda_integration
    )
    
    # Create WebSocket API for real-time communication
    websocket_api = apigw_v2.WebSocketApi(
        scope, "ChainlitWebSocketApi",
        route_selection_expression="$request.body.action"
    )
    
    # Add WebSocket Lambda integration
    websocket_stage = apigw_v2.WebSocketStage(
        scope, "ChainlitWebSocketStage",
        web_socket_api=websocket_api,
        stage_name="prod",
        auto_deploy=True
    )
    
    # Add default route (required for WebSocket APIs)
    websocket_api.add_route(
        "connect",
        integration=apigw_integrations.WebSocketLambdaIntegration(
            "ConnectIntegration", handler=lambda_function
        )
    )
    
    websocket_api.add_route(
        "disconnect",
        integration=apigw_integrations.WebSocketLambdaIntegration(
            "DisconnectIntegration", handler=lambda_function
        )
    )
    
    websocket_api.add_route(
        "default",
        integration=apigw_integrations.WebSocketLambdaIntegration(
            "DefaultIntegration", handler=lambda_function
        )
    )