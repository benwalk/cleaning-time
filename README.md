# Cleaning Time

## Development

This app is an AWS Lambda function and the source is in `src/main.py`. Tests for this function are in `src/test_main.py`.

## Test

Assuming `python3` is aliased to a python 3.8 version, you can run tests by executing
```
python3 -m unittest test_main.py
```
from the `src/` directory in your terminal.

Additionally, with [python-lambda-local](https://pypi.org/project/python-lambda-local/) installed, you can run
```
python-lambda-local -f handler main.py ./test_event.json
```
from the `src/` directory to simulate a lambda event.


## Deployment

`src/main.py` is deployed as an AWS Lambda function, and the terraform directory contains the infrastructure definition that manages the AWS resources for it.

To deploy your own version of this app, first ensure your AWS credentials are properly configured (both permissions and that they exist in your environment), e.g.,
```
export AWS_ACCESS_KEY_ID="anaccesskey"
export AWS_SECRET_ACCESS_KEY="asecretkey"
export AWS_DEFAULT_REGION="us-west-2"
```
and then from `./terraform/`,
```
terraform apply
```

The output will provide you with the endpoint to the newly created lambda function.

Usage instructions are bundled within the app and can be found by navigating to the lambda function in your browser.
