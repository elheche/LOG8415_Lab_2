import sys

from mypy_boto3_iam import IAMClient


def get_role(iam: IAMClient, role_name: str) -> str:
    try:
        print('Getting role arn...')
        response = iam.get_role(RoleName=role_name)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        role_arn = response['Role']['Arn']
        print(f'Role arn obtained successfully.\n{role_arn}')
        return role_arn
