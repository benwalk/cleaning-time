# URL for the lambda function, e.g. "/test"
output "base_url" {
  value = aws_api_gateway_deployment.cleaning_time.invoke_url
}
