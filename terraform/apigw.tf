# The "REST API" is the container for all of the other API Gateway objects we will create.
resource "aws_api_gateway_rest_api" "cleaning_time" {
  name        = "cleaning-time"
  description = "Terraform Serverless Application"
}

# All incoming requests to API Gateway must match with a configured resource and method in order to be handled.
# The special path_part value "{proxy+}" activates proxy behavior, which means that this resource will match any request path. Similarly, the aws_api_gateway_method block uses a http_method of "ANY", which allows any request method to be used. Taken together, this means that all incoming requests will match this resource.
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.cleaning_time.id
  parent_id   = aws_api_gateway_rest_api.cleaning_time.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.cleaning_time.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# Each method on an API gateway resource has an integration which specifies where incoming requests are routed.
# Requests to this method should be sent to the lambda function defined above
# The AWS_PROXY integration type causes API gateway to call into the API of another AWS service.
resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.cleaning_time.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.cleaning_time.invoke_arn
}

# the proxy resource cannot match an empty path at the root of the API. To handle that, a similar configuration must be applied to the root resource
resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.cleaning_time.id
  resource_id   = aws_api_gateway_rest_api.cleaning_time.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.cleaning_time.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.cleaning_time.invoke_arn
}

# an API Gateway "deployment" in order to activate the configuration and expose the API at a URL that can be used for testing
resource "aws_api_gateway_deployment" "cleaning_time" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.cleaning_time.id
  stage_name  = "cleaning-time"
}

# Explicitly grant Lambda access from API Gateway
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cleaning_time.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.cleaning_time.execution_arn}/*/*"
}
