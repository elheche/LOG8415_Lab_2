import sys

import boto3
from typing import Literal


def create_aws_service(
        aws_service_name: Literal['ec2', 'elbv2', 'codedeploy', 'cloudwatch', 'iam', 's3', 'sts'],
        aws_region_name: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None
):
    try:
        print(f'Creating {aws_service_name} service...')
        aws_service = boto3.client(
            service_name=aws_service_name,
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'{aws_service_name} service created successfully.')
        return aws_service
