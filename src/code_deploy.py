import sys

from mypy_boto3_codedeploy import CodeDeployClient


def create_application(code_deploy: CodeDeployClient, application_name: str) -> str:
    try:
        print('Creating application...')
        response = code_deploy.create_application(
            applicationName=application_name,
            computePlatform='Server'
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        application_id = response['applicationId']
        print(f'Application created successfully.\n{application_id}')
        return application_id


def create_deployment_group(code_deploy: CodeDeployClient, code_deploy_config: dict, service_role_arn: str) -> str:
    try:
        print('Creating deployment group...')
        response = code_deploy.create_deployment_group(
            applicationName=code_deploy_config['ApplicationName'],
            deploymentGroupName=code_deploy_config['DeploymentGroupName'],
            deploymentConfigName=code_deploy_config['DeploymentConfigName'],
            ec2TagFilters=code_deploy_config['EC2TagFilters'],
            serviceRoleArn=service_role_arn,
            autoRollbackConfiguration=code_deploy_config['AutoRollbackConfiguration'],
            deploymentStyle=code_deploy_config['DeploymentStyle']
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        deployment_group_id = response['deploymentGroupId']
        print(f'Deployment group created successfully.\n{deployment_group_id}')
        return deployment_group_id


def create_deployment(code_deploy: CodeDeployClient, bucket: str, code_deploy_config: dict) -> str:
    revision = code_deploy_config['Revision']
    revision['s3Location']['bucket'] = bucket
    try:
        print('Launching application deployment...')
        response = code_deploy.create_deployment(
            description=f'Deploy a simple flask server to {code_deploy_config["DeploymentGroupName"]}',
            applicationName=code_deploy_config['ApplicationName'],
            deploymentGroupName=code_deploy_config['DeploymentGroupName'],
            revision=revision
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        deployment_id = response['deploymentId']
        print(f'Application deployment launched successfully.\n{deployment_id}')
        return deployment_id


def delete_application(code_deploy: CodeDeployClient, application_name: str) -> None:
    try:
        print('Deleting application...')
        code_deploy.delete_application(
            applicationName=application_name,
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Application deleted successfully.\n{application_name}')
