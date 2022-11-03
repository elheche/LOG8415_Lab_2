import argparse
import json
from ec2 import *
from init_aws_service import *
from ssh_run_command import *


def main() -> None:
    """
    this function runs the whole experience : creates and configures the AWS EC2 instances and runs the map reduce experiences
    (WordCount and Social Network)
    """
    ###################################################################################################################
    #                                    Setting program arguments
    ###################################################################################################################

    parser = argparse.ArgumentParser(
        description=('Program that set up Hadoop (latest version) and Spark (v2.0.0) on a M4.large Linux Ubuntu instance. '
                     'It first looks for credentials and configuration files provided by your AWS CLI '
                     '(You can configure your AWS CLI using this command: <aws configure>). '
                     'If not found, it offers you the option to manually enter their values using '
                     'the arguments below:'
                     )
    )

    sub_parser = parser.add_subparsers(title='aws arguments', dest='AWS')
    aws_parser = sub_parser.add_parser('aws')

    parser.add_argument('-r', '--reset', help="reset user's aws account.", dest='RESET', required=False, action='store_true')
    aws_parser.add_argument('-g', '--region', help='region name for your AWS account.', dest='AWS_REGION_NAME', required=True, nargs=1)
    aws_parser.add_argument('-i', '--id', help='access key for your AWS account.', dest='AWS_ACCESS_KEY_ID', required=True, nargs=1)
    aws_parser.add_argument('-s', '--secret', help='secret key for your AWS account.', dest='AWS_SECRET_ACCESS_KEY', required=True, nargs=1)
    aws_parser.add_argument('-t', '--token', help='session key for your AWS account.', dest='AWS_SESSION_TOKEN', required=True, nargs=1)

    args = parser.parse_args()

    ###################################################################################################################
    #                                    Initializing AWS services
    ###################################################################################################################

    if args.AWS:
        user_credentials_config = [
            args.AWS_REGION_NAME[0],
            args.AWS_ACCESS_KEY_ID[0],
            args.AWS_SECRET_ACCESS_KEY[0],
            args.AWS_SESSION_TOKEN[0]
        ]

        # Initialize aws services with user credentials and configuration
        ec2 = create_aws_service(EC2_CONFIG['Common']['ServiceName'], *user_credentials_config)

    else:
        credentials_exists = Path(f'{Path.home()}/.aws/credentials').is_file()
        config_exists = Path(f'{Path.home()}/.aws/config').is_file()

        if credentials_exists and config_exists:
            # Initialize aws services with default credentials and configuration
            ec2 = create_aws_service(EC2_CONFIG['Common']['ServiceName'])
        else:
            parser.error('default aws credentials and configuration not found.')
            sys.exit(1)

    ###################################################################################################################
    #                                    Resetting AWS account
    ###################################################################################################################

    if args.RESET:
        reset(ec2)
        sys.exit(0)

    ###################################################################################################################
    #                                    Creating and Configuring EC2 instance
    ###################################################################################################################

    # Get the default vpc id
    vpc_id = get_vpc_id(ec2)

    # Create a security group and set its inbound rules to accept HTTP and SSH connections
    security_group_id = create_security_group(ec2, vpc_id, EC2_CONFIG['Common']['SecurityGroups'][0])
    set_security_group_inbound_rules(ec2, security_group_id)

    # Save security group id to aws_data (needed to reset aws account)
    aws_data = {'SecurityGroupId': security_group_id}

    # Create a key pair
    key_pair_id = create_key_pair(ec2, EC2_CONFIG['Common']['KeyPairName'])

    # Save key pair id to aws_data (needed to reset aws account)
    aws_data['KeyPairId'] = key_pair_id

    # Create one instance of m4.large running linux ubuntu
    instance_tag_id = "1"
    ec2_instance_id = launch_ec2_instance(ec2, EC2_CONFIG['Common'] | EC2_CONFIG['Cluster1'], instance_tag_id)

    # Save ec2 instance id to aws_data (needed to reset aws account)
    aws_data['EC2InstanceIds'] = [ec2_instance_id]

    # Wait until all ec2 instance state pass to 'running'
    wait_until_all_ec2_instance_are_running(ec2, [ec2_instance_id])

    # Get ec2 instance public ipv4 address
    ec2_instance_public_ipv4_address = get_ec2_instance_public_ipv4_address(ec2, ec2_instance_id)

    # Save ec2 instance public ipv4 address to aws_data (needed to connect to it via ssh)
    aws_data['EC2InstancePublicIPv4Address'] = ec2_instance_public_ipv4_address

    # Export aws_data to aws_data.json file (needed to execute -r/--reset command)
    save_aws_data(aws_data, 'aws_data.json')

    ###################################################################################################################
    #                                    Running commands via SSH
    ###################################################################################################################

    # Copy the necessary files and run setup.sh on the created EC2 instance
    ssh_run_commands(ec2_instance_public_ipv4_address)


def save_aws_data(aws_data: dict, path: str) -> None:
    """
    export AWS data to a json file needed to run a reset command

    :param aws_data: The data of aws elements created during program execution
    :param path: The path where to save the data
    :returns: None
    """
    try:
        print('Saving aws data...')
        with open(path, 'w') as file:
            json.dump(aws_data, file)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'AWS data saved successfully to {path}.')


def load_aws_data(path: str) -> dict:
    """
    load AWS data from a json file

    :param path: The path where to find the data
    :return: The aws data as a dictionary
    """
    try:
        print('Loading aws data...')
        with open(path, 'r') as file:
            aws_data = json.load(file)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'AWS data loaded successfully.\n{aws_data}')
        return aws_data


def reset(ec2: EC2Client) -> None:
    """
    Reset your AWS account by terminating and deleting all the elements created during program execution

    :param ec2: The AWS EC2 client to be reset
    """
    data_exists = Path('aws_data.json').is_file()

    if data_exists:
        aws_data = load_aws_data('aws_data.json')
        terminate_ec2_instances(ec2, aws_data['EC2InstanceIds'])
        wait_until_all_ec2_instances_are_terminated(ec2, aws_data['EC2InstanceIds'])
        delete_key_pair(ec2, aws_data['KeyPairId'])
        delete_security_group(ec2, aws_data['SecurityGroupId'])
        print('AWS account successfully reset.')
    else:
        print('aws_data.json file not found.')


if __name__ == '__main__':
    main()
