import sys
import time
import paramiko
from pathlib import Path
from paramiko.client import SSHClient
from config import *


def ssh_connect(ssh_client: SSHClient, ec2_instance_public_ipv4_address: str) -> None:
    """
    connect to an EC2 instance through SSH

    :param ssh_client: The SSH client
    :param ec2_instance_public_ipv4_address: The public IPv4 address of the EC2 instance to which we are connecting
    :return: None
    """

    max_attempt = 10
    attempt = 1

    while True:
        try:
            print(f'Establishing an SSH connection to EC2 Instance... \nAttempt: {attempt}')
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.RSAKey.from_private_key_file(SSH_CONFIG['KeyPairFile'])
            ssh_client.connect(
                hostname=ec2_instance_public_ipv4_address,
                username=SSH_CONFIG['EC2UserName'],
                pkey=private_key
            )
        except Exception as e:
            if attempt < max_attempt:
                attempt += 1
                time.sleep(5)  # wait 5s between each attempt.
            else:
                print(e)
                sys.exit(1)
        else:
            print(f"SSH connection successfully established to EC2 instance:\n{ec2_instance_public_ipv4_address}")
            break


def ssh_upload(ssh_client: SSHClient, local_path: str, remote_path: str) -> None:
    """
    upload a file to an EC2 instance through SSH

    :param ssh_client: The SSH client
    :param local_path: The file path to upload from the local machine
    :param remote_path: The file path to which it is uploaded on the EC2 instance
    :return: None
    """

    try:
        print(f'Uploading a file to EC2 Instance...')
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(local_path, remote_path)
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        sftp_client.close()
        print(f'File successfully uploaded to EC2 instance:\n{Path(local_path).name}')


def ssh_run_commands(ec2_instance_public_ipv4_address: str) -> None:
    """
    connect to an EC2 instance, upload WordCount and Social Network files, and run the setup script on it via SSH

    :param ec2_instance_public_ipv4_address: The public IPv4 address of the EC2 instance to which we are connecting
    :return: None
    """
    ssh_client = paramiko.SSHClient()

    ssh_connect(ssh_client, ec2_instance_public_ipv4_address)

    for local_path in SSH_CONFIG['FilesToUpload']:
        remote_path = str(Path(SSH_CONFIG['RemoteDirectory']).joinpath(Path(local_path).name))
        ssh_upload(ssh_client, local_path, remote_path)

    _, stdout, stderr = ssh_client.exec_command(
        f"chmod +x {SSH_CONFIG['ScriptToExecute']} && {SSH_CONFIG['ScriptToExecute']}",
        get_pty=True
    )

    for line in iter(stdout.readline, ""):
        print(line, end="")
