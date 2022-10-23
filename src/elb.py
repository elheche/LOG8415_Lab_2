import sys
from datetime import datetime
from typing import Tuple, Dict, Union, List

from mypy_boto3_elbv2 import ElasticLoadBalancingv2Client


def create_target_group(
        elbv2: ElasticLoadBalancingv2Client,
        target_group_name: str,
        vpc_id: str
) -> str:
    try:
        print('Creating target group...')
        response = elbv2.create_target_group(
            Name=target_group_name,
            Protocol='HTTP',
            ProtocolVersion='HTTP1',
            Port=80,
            VpcId=vpc_id,
            HealthCheckProtocol='HTTP',
            TargetType='instance',
            IpAddressType='ipv4'
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
        print(f'Target group created successfully.\n{target_group_arn}')
        return target_group_arn


def register_targets(
        elbv2: ElasticLoadBalancingv2Client,
        target_group_arn: str,
        ec2_instance_ids: list[str]
) -> None:
    try:
        print('Registering targets...')
        elbv2.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': ec2_instance_id, 'Port': 80} for ec2_instance_id in ec2_instance_ids]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Targets registered successfully to group target {target_group_arn}.\n{ec2_instance_ids}')


def create_application_load_balancer(
        elbv2: ElasticLoadBalancingv2Client,
        subnets: list[str],
        security_group_ids: list[str]
) -> tuple[str, str]:
    try:
        print('Creating application load_balancer...')
        response = elbv2.create_load_balancer(
            Name='log8415-lab1-elb',
            Subnets=subnets,
            SecurityGroups=security_group_ids,
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        alb_dns_name = response['LoadBalancers'][0]['DNSName']
        print(f'Application load balancer created successfully.\n{alb_arn}')
        return alb_arn, alb_dns_name


def create_alb_listener(
        elbv2: ElasticLoadBalancingv2Client,
        alb_arn: str,
        target_group_arns: list[str]
) -> str:
    try:
        print('Creating alb listener...')
        response = elbv2.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'ForwardConfig': {
                        'TargetGroups': [
                            {
                                'TargetGroupArn': target_group_arns[0],
                                'Weight': 50
                            },
                            {
                                'TargetGroupArn': target_group_arns[1],
                                'Weight': 50
                            }
                        ]
                    }
                }
            ]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        alb_listener_arn = response['Listeners'][0]['ListenerArn']
        print(f'ALB listener created successfully.\n{alb_listener_arn}')
        return alb_listener_arn


def create_alb_listener_rule(
        elbv2: ElasticLoadBalancingv2Client,
        alb_listener_arn: str,
        target_group_arn: str,
        path_pattern: str,
        priority: int
) -> str:
    try:
        print('Creating alb listener rule...')
        response = elbv2.create_rule(
            ListenerArn=alb_listener_arn,
            Conditions=[
                {
                    'Field': 'path-pattern',
                    'Values': [
                        path_pattern
                    ]
                }
            ],
            Priority=priority,
            Actions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': target_group_arn
                }
            ]
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        alb_listener_rule_arn = response['Rules'][0]['RuleArn']
        print(f'ALB listener rule created successfully.\n{alb_listener_rule_arn}')
        return alb_listener_rule_arn


def delete_alb_listener_rule(
        elbv2: ElasticLoadBalancingv2Client,
        rule_arn: str,
) -> None:
    try:
        print('Deleting ALB listener rule...')
        elbv2.delete_rule(
            RuleArn=rule_arn
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'ALB listener rule deleted successfully.\n{rule_arn}')


def delete_alb_listener(
        elbv2: ElasticLoadBalancingv2Client,
        alb_listener_arn: str,
) -> None:
    try:
        print('Deleting ALB listener...')
        elbv2.delete_listener(
            ListenerArn=alb_listener_arn
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'ALB listener deleted successfully.\n{alb_listener_arn}')


def delete_application_load_balancer(
        elbv2: ElasticLoadBalancingv2Client,
        load_balancer_arn: str,
) -> None:
    try:
        print('Deleting application load_balancer...')
        elbv2.delete_load_balancer(
            LoadBalancerArn=load_balancer_arn
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Application load balancer deleted successfully.\n{load_balancer_arn}')


def wait_until_alb_is_deleted(
        elbv2: ElasticLoadBalancingv2Client,
        load_balancer_arn: str
) -> None:
    try:
        print('Waiting until alb is deleted...')
        waiter = elbv2.get_waiter('load_balancers_deleted')
        waiter.wait(
            LoadBalancerArns=[load_balancer_arn],
            WaiterConfig={'Delay': 10}  # wait 10s between each attempt.
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print('ALB is now deleted.')


def delete_target_group(
        elbv2: ElasticLoadBalancingv2Client,
        target_group_arn: str,
) -> None:
    try:
        print('Deleting target group...')
        elbv2.delete_target_group(
            TargetGroupArn=target_group_arn
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print(f'Target Group deleted successfully.\n{target_group_arn}')
