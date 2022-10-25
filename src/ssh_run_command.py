import time
import boto3
import jmespath
import paramiko


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
        return True
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(instance_ip))
        ssh_connexion(ssh, instance_ip, retries)


def run_command() -> None:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    public_ip = get_all_instance_ip()
    ssh_connexion(ssh, public_ip, 0)
    commands = [
        "git clone https://github.com/foalem/WordCount.git",
        "chmod u+x WordCount/setup.sh",
        # "sed -i -e 's/\r$//' /WordCount/setup.sh",
        "Cd /WordCount"
        "/setup.sh"
    ]
    for command in commands:
        print("running command: {}".format(command))
        stdin, stdout, stderr = ssh.exec_command(command)
        print('stdout:', stdout.read())
        print('stderr:', stderr.read())


if __name__ == "__main__":
    run_command()
