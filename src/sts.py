import sys

from mypy_boto3_sts import STSClient


def get_aws_user_account(sts: STSClient) -> str:
    try:
        print('Getting AWS user account...')
        response = sts.get_caller_identity()
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        aws_user_account = response['Account']
        print(f'AWS user account obtained successfully.\n{aws_user_account}')
        return aws_user_account
