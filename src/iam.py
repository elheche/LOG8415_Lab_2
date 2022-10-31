import sys

from mypy_boto3_iam import IAMClient


def get_role(iam: IAMClient, role_name: str) -> str:
    """
    get the Amazon Resource Names role of IAM (necessary for Code Deploy)
    :param iam: IAM Client instance
    :param role_name: the role name
    :return: the Amazon Resource Names role of IAM
    """
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
