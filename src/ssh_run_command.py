import time
import boto3
import jmespath
import paramiko
import shutil
import os
from main import load_aws_data

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

FILE_NAME_r = "recommandfriend"
FILE_NAME = "wordcount"
PATH = os.path.join(ROOT_DIR, FILE_NAME)
TO_RUN = './setup.sh'
KEY_SOURCE = 'ec2_keypair.pem'
KEY_DESTINATION = 'wordcount/'
KEY_DESTINATION_r = 'recommandfriend/'


def copy_key_pair() -> None:
    try:
        shutil.copy2(KEY_SOURCE, KEY_DESTINATION)
        print("File copied successfully.")
        time.sleep(5)

    # If source and destination are same
    except shutil.SameFileError:
        print("Source and destination represents the same file.")

    # If destination is a directory.
    except IsADirectoryError:
        print("Destination is a directory.")

    # If there is any permission issue
    except PermissionError:
        print("Permission denied.")

    # For other errors
    except Exception as e:
        print("Error occurred while copying file.{}".format(e))


def get_all_instance_ip() -> int:
    client = boto3.client('ec2')
    response = client.describe_instances(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
            ]
        },
    ], )

    public_dns_ip = jmespath.search("Reservations[].Instances[].PublicIpAddress", response)
    print(public_dns_ip[0])
    return public_dns_ip[0]


def ssh_connexion(ssh, instance_ip, retries) -> bool:
    if retries > 3:
        return False

    privkey = paramiko.RSAKey.from_private_key_file(
        'ec2_keypair.pem')
    interval = 5
    try:
        retries += 1
        print(f'SSH into the instance: {instance_ip}')
        ssh.connect(hostname=instance_ip,
                    username='ubuntu', pkey=privkey)
        sftp = ssh.open_sftp()
        # Upload files
        sftp.put('./setup.sh', '/home/ubuntu/setup.sh')
        sftp.put('./wordcount/WordCount.java', '/home/ubuntu/WordCount.java')
        sftp.put('./recommandfriend/FriendSocialNetwork.java', '/home/ubuntu/FriendSocialNetwork.java')
        sftp.put('./recommandfriend/soc-LiveJournal1Adj.txt', '/home/ubuntu/soc-LiveJournal1Adj.txt')
        return True
    except Exception as e:
        print(e)
        time.sleep(interval)
        print(f'Retrying SSH connection to {instance_ip}')
        ssh_connexion(ssh, instance_ip, retries)
        return False


def run_command() -> None:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ec2_public_ipv4 = load_aws_data('./aws_data.json')['EC2InstancePublicIPv4Address']
    ssh_connexion(c, ec2_public_ipv4, 0)

    c.exec_command(f'chmod +x {TO_RUN}')
    stdin, stdout, stderr = c.exec_command(TO_RUN, get_pty=True)

    for line in iter(stdout.readline, ""):
        print(line, end="")
