"""
create_test_environment

Extracted from book: cloud test environment deployment example (boto3).
This is a simplified helper and may require AWS credentials and valid config.
"""
import boto3
import json


def create_test_environment(config_file):
    # 读取配置
    with open(config_file, 'r') as f:
        config = json.load(f)

    # 创建EC2客户端
    ec2 = boto3.resource('ec2', region_name=config['region'],
                         aws_access_key_id=config.get('access_key'),
                         aws_secret_access_key=config.get('secret_key'))

    # 创建安全组
    security_group = ec2.create_security_group(GroupName=config['sg_name'],
                                               Description='Security group for test environment')

    # 配置安全组规则（示例）
    security_group.authorize_ingress(IpPermissions=[
        {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ])

    # 启动EC2实例
    instances = ec2.create_instances(ImageId=config['ami_id'], MinCount=1, MaxCount=config['instance_count'],
                                     InstanceType=config['instance_type'], KeyName=config['key_name'],
                                     SecurityGroupIds=[security_group.id])

    print(f"创建了 {len(instances)} 个EC2实例")
    for instance in instances:
        print(f"实例ID: {instance.id}")

    return instances


if __name__ == '__main__':
    # usage: python create_test_environment.py config.json
    import sys
    if len(sys.argv) < 2:
        print('usage: python create_test_environment.py config.json')
        sys.exit(2)
    create_test_environment(sys.argv[1])
