EC2_CONFIG = {
    'Common': {
        'ServiceName': 'ec2',
        'ImageId': 'ami-0ee23bfc74a881de5',  # Ubuntu, 18.04 LTS, 64-bit (x86) (CodeDeploy Agent preinstalled)
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
