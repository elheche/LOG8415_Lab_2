import time
import boto3
import jmespath
import paramiko
import shutil
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

FILE_NAME = "wordcount"
PATH = os.path.join(ROOT_DIR, FILE_NAME)
TO_RUN = 'setup.sh'
ZIP_FILE = shutil.make_archive(FILE_NAME, 'zip', FILE_NAME)
ZIP_FILE_NAME = FILE_NAME + '.zip'
KEY_SOURCE = 'ec2_keypair.pem'
KEY_DESTINATION = 'wordcount/'


def copy_key_pair() -> None:
    try:
        shutil.copy(KEY_SOURCE, KEY_DESTINATION)
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


def ssh_connexion(ssh, instance_ip, retries) -> None:
    if retries > 3:
        return False
    privkey = paramiko.RSAKey.from_private_key_file(
        'ec2_keypair.pem')
    interval = 5
    try:
        retries += 1
        print('SSH into the instance: {}'.format(instance_ip))
        ssh.connect(hostname=instance_ip,
                    username='ubuntu', pkey=privkey)
        sftp = ssh.open_sftp()
        # Upload zip file
        upload = sftp.put(ZIP_FILE, '/home/ubuntu/' + ZIP_FILE_NAME)
        return True
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(instance_ip))
        ssh_connexion(ssh, instance_ip, retries)


def run_command() -> None:
    copy_key_pair()
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    public_ip = get_all_instance_ip()
    ssh_connexion(c, public_ip, 0)
    commands = [
        'sudo apt-get update -y',
        'sudo apt install unzip',
        'unzip -o ' + FILE_NAME,
        'bash sample.sh',
        'chmod u+x ./' + TO_RUN,
        './' + TO_RUN,
        'sudo scp -i ec2_keypair.pem ubuntu@' + str(get_all_instance_ip()) + ':/home/ubuntu/time.txt .src/wordcount']
    for command in commands:
        print("running command: {}".format(command))
        stdin, stdout, stderr = c.exec_command(command)
        print('stdout:', stdout.read())
        print('stderr:', stderr.read())
