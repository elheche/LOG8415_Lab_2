EC2_CONFIG = {
    'Common': {
        'ServiceName': 'ec2',
        'ImageId': 'ami-08c40ec9ead489470',  # Ubuntu, 22.04 LTS, 64-bit (x86)
        'KeyPairName': 'log8415_lab1_kp',
        'SecurityGroups': ['log8415_lab1_sg'],
        'InstanceCount': 1,
        'InstanceProfileName': 'LabInstanceProfile',  # We'll use this default role since we can't create a new one.
        'MetadataOptions': {
            'InstanceMetadataTags': 'enabled'
        }
    },
    'Cluster1': {
        'InstanceType': 'm4.large',
        'AvailabilityZone': 'us-east-1a',
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Cluster', 'Value': '1', },
                    {'Key': 'Instance', 'Value': '', }  # Instance tag value is given when creating the instance
                ]
            }
        ]
    },
    'Cluster2': {
        'InstanceType': 't2.large',
        'AvailabilityZone': 'us-east-1b',
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Cluster', 'Value': '2', },
                    {'Key': 'Instance', 'Value': '', }  # Instance tag value is given when creating the instance
                ]
            }
        ]
    }
}

SSH_CONFIG = {
    'EC2UserName': 'ubuntu',
    'KeyPairFile': 'ec2_keypair.pem',
    'FilesToUpload': [
        './setup.sh',
        './wordcount/WordCount.java',
        './recommandfriend/FriendSocialNetwork.java',
        './recommandfriend/soc-LiveJournal1Adj.txt'
    ],
    'RemoteDirectory': '/home/ubuntu/',
    'ScriptToExecute': './setup.sh'
}
