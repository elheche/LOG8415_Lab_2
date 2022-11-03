import sys
import time

from botocore.exceptions import ClientError
from mypy_boto3_ec2 import EC2Client


def get_vpc_id(ec2: EC2Client) -> str:
    """
    get the Amazon Virtual Private Cloud's unique ID

    :param ec2: EC2 Client
    :return: Virtual Private Cloud's unique ID
    """
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
    """
    create a security group

    :param ec2: EC2 Client
    :param vpc_id: Virtual Private Cloud's unique ID
    :param group_name: the group's name
    :return: security group's unique ID
    """
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
    """
    set the security group's inbound rules

    :param ec2: EC2 Client
    :param security_group_id: security group's unique ID
    :return: None
    """
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
    """
    create key pair of EC2 instance

    :param ec2: EC2 Client
    :param key_name: key unique name
    :return: key pair id
    """
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
    """
    launch an ec2 instance

    :param ec2: EC2 Client
    :param ec2_config: EC2 instance configuration
    :param instance_tag_id: EC2 instance id tag
    :return: EC2 instance unique ID
    """

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
    """
    wait until EC2 instance state change to "running"

    :param ec2: EC2 Client
    :param instance_ids: EC2 instance ids to wait
    :return: None
    """
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


def terminate_ec2_instances(
        ec2: EC2Client,
        ec2_instance_ids: list[str]
) -> None:
    """
    terminate an EC2 instance

    :param ec2: EC2 Client
    :param ec2_instance_ids: EC2 instance ids to terminate
    :return: None
    """

    try:
        print('Terminating EC2 instances...')
        ec2.terminate_instances(InstanceIds=ec2_instance_ids)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'EC2 instances terminated successfully.\n{ec2_instance_ids}')


def delete_key_pair(ec2: EC2Client, key_pair_id: str) -> None:
    """
    delete a key pair

    :param ec2: EC2 Client
    :param key_pair_id: key pair id to delete
    :return: None
    """

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
    """
    delete a security group

    :param ec2: EC2 Client
    :param security_group_id: security group id to delete
    :return: None
    """

    max_attempt = 10
    attempt = 1

    while True:
        try:
            print(f'Deleting security group...\nAttempt: {attempt}')
            ec2.delete_security_group(
                GroupId=security_group_id
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DependencyViolation' and attempt < max_attempt:
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
    """
    wait until EC2 instance state change to "terminated"

    :param ec2: EC2 Client
    :param instance_ids: EC2 instance ids to wait
    :return: None
    """

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
    """
    get the EC2 instance's public IPv4 address

    :param ec2: EC2 Client
    :param ec2_instance_id: EC2 instance id
    :return: EC2 instance public IPv4 address
    """

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
