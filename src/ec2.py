import sys
import time

from botocore.exceptions import ClientError
from mypy_boto3_ec2 import EC2Client


def get_vpc_id(ec2: EC2Client) -> str:
    try:
        print('Getting vpc id...')
        response = ec2.describe_vpcs()
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
        print(f'vpc id obtained successfully.\n{vpc_id}')
        return vpc_id


def create_security_group(ec2: EC2Client, vpc_id: str, group_name: str) -> str:
    try:
        print('Creating security group...')
        response = ec2.create_security_group(
            GroupName=group_name,
            Description='Allow SSH & HTTP access to the server.',
            VpcId=vpc_id
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        security_group_id = response['GroupId']
        print(f'Security group created successfully.\n{security_group_id}')
        return security_group_id


def set_security_group_inbound_rules(ec2: EC2Client, security_group_id: str) -> None:
    try:
        print('Setting inbound rules...')
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',  # Type: SSH
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                 },
                {'IpProtocol': 'tcp',  # Type: HTTP
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                 },
            ]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Inbound rules successfully set for {security_group_id}')


def create_key_pair(ec2: EC2Client, key_name: str) -> str:
    try:
        print('Creating key pair...')
        with open('ec2_keypair.pem', 'w') as file:
            key_pair = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
            file.write(key_pair.get('KeyMaterial'))
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        key_pair_id = key_pair.get('KeyPairId')
        print(f'Key pair created successfully.\n{key_pair_id}')
        return key_pair_id


def launch_ec2_instance(ec2: EC2Client, ec2_config: dict, instance_tag_id: str) -> str:
    # Add a unique tag to each ec2 instance
    ec2_config['TagSpecifications'][0]['Tags'][1]['Value'] = instance_tag_id
    try:
        print('Creating EC2 instance...')
        response = ec2.run_instances(
            ImageId=ec2_config['ImageId'],
            MinCount=ec2_config['InstanceCount'],
            MaxCount=ec2_config['InstanceCount'],
            InstanceType=ec2_config['InstanceType'],
            KeyName=ec2_config['KeyPairName'],
            SecurityGroups=ec2_config['SecurityGroups'],
            Placement={
                'AvailabilityZone': ec2_config['AvailabilityZone']
            },
            TagSpecifications=ec2_config['TagSpecifications'],
            IamInstanceProfile={
                'Name': ec2_config['InstanceProfileName']
            },
            MetadataOptions=ec2_config['MetadataOptions']
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        ec2_instances_id = response['Instances'][0]['InstanceId']
        print(f'EC2 instance created successfully.\n{ec2_instances_id}')
        return ec2_instances_id


def wait_until_all_ec2_instance_are_running(ec2: EC2Client, instance_ids: list[str]) -> None:
    try:
        print('Waiting until all ec2 instances are running...')
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(
            InstanceIds=instance_ids,
            WaiterConfig={'Delay': 10}  # wait 10s between each attempt.
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print('All EC2 instances are now running.')


def get_subnet_ids(ec2: EC2Client, vpc_id: str, availability_zone: list[str]) -> list[str]:
    try:
        print('Getting subnet ids...')
        response = ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [vpc_id],
                },
                {
                    'Name': 'availability-zone',
                    'Values': availability_zone,
                }
            ]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]
        print(f'Subnet ids obtained successfully.\n{subnet_ids}')
        return subnet_ids


def add_tag_to_ec2_instance(ec2: EC2Client, ec2_instance_id: str, tag: dict) -> None:
    try:
        print('Adding a tag to an ec2 instance...')
        ec2.create_tags(
            Resources=[ec2_instance_id],
            Tags=[
                {
                    'Key': tag['Key'],
                    'Value': tag['Value']
                }
            ]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Tag successfully added to ec2 instance {ec2_instance_id}.')


def reboot_all_ec2_instances(ec2: EC2Client, ec2_instance_ids: list[str]) -> None:
    try:
        print('Rebooting all ec2 instances...')
        ec2.reboot_instances(InstanceIds=ec2_instance_ids)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'All ec2 instances rebooted successfully.\n{ec2_instance_ids}')


def terminate_ec2_instances(
        ec2: EC2Client,
        ec2_instance_ids: list[str]
) -> None:
    try:
        print('Terminating EC2 instances...')
        ec2.terminate_instances(InstanceIds=ec2_instance_ids)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'EC2 instances terminated successfully.\n{ec2_instance_ids}')


def delete_key_pair(ec2: EC2Client, key_pair_id: str) -> None:
    try:
        print('Deleting key pair...')
        ec2.delete_key_pair(
            KeyPairId=key_pair_id
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Key pair deleted successfully.\n{key_pair_id}')


def delete_security_group(ec2: EC2Client, security_group_id: str) -> None:
    MAX_ATTEMPT = 10
    attempt = 1

    while (True):
        try:
            print(f'Deleting security group...\nAttempt: {attempt}')
            ec2.delete_security_group(
                GroupId=security_group_id
            )
        except ClientError as e:
            if (e.response['Error']['Code'] == 'DependencyViolation' and attempt < MAX_ATTEMPT):
                attempt += 1
                time.sleep(10)  # wait 10s between each attempt.
            else:
                print(e)
                sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        else:
            print(f'Security Group deleted successfully.\n{security_group_id}')
            break


def wait_until_all_ec2_instances_are_terminated(ec2: EC2Client, instance_ids: list[str]) -> None:
    try:
        print('Waiting until all ec2 instances are terminated...')
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait(
            InstanceIds=instance_ids,
            WaiterConfig={'Delay': 10}  # wait 10s between each attempt.
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print('All EC2 instances are now terminated.')


def get_ec2_instance_public_ipv4_address(ec2: EC2Client, ec2_instance_id: str) -> str:
    try:
        print('Getting ec2 instance public ipv4 address...')
        response = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [ec2_instance_id],
                }
            ]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        ec2_instance_public_ipv4_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        print(f'EC2 instance public ipv4 address obtained successfully.\n{ec2_instance_public_ipv4_address}')
        return ec2_instance_public_ipv4_address
