from time import sleep

import os
import uuid
import tempfile

import boto3
import pytest
import testinfra

from botocore.exceptions import ClientError

AMI_ID = os.getenv('AMI_ID')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION')
SSH_USERNAME = os.getenv('SSH_USERNAME', 'ubuntu')
INSTANCE_TYPE = os.getenv('INSTANCE_TYPE', 't2.small')

# Override the 'host' fixture with an EC2 instance launched from the AMI
@pytest.fixture
def host():
    ec2_client = boto3.client('ec2', region_name=AWS_REGION)

    test_sg, keypair_name, key_path = _setup_ec2_environment(ec2_client)

    request = ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        SecurityGroupIds=[
            test_sg,
        ],
        KeyName=keypair_name,
        MinCount=1,
        MaxCount=1
    )

    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(
        InstanceIds=[
            request['Instances'][0]['InstanceId']
        ]
    )
    sleep(30)

    request = ec2_client.describe_instances(
        InstanceIds=[
            request['Instances'][0]['InstanceId']
        ]
    )

    ssh_config_path = _setup_ssh_config(key_path)
    instance = request['Reservations'][0]['Instances'][0]
    yield testinfra.get_host("ssh://" + instance['PublicIpAddress'],
                             ssh_config=ssh_config_path
                            )

    ec2_client.terminate_instances(
        InstanceIds=[
            instance['InstanceId']
        ]
    )

    waiter = ec2_client.get_waiter('instance_terminated')
    waiter.wait(
        InstanceIds=[
            instance['InstanceId']
        ]
    )

    _cleanup_ec2_environment(ec2_client, test_sg, keypair_name, key_path)
    os.remove(ssh_config_path)


def _setup_ec2_environment(client):
    security_group_id = _create_security_group(client)
    key_name, key_path = _create_ssh_keypair(client)

    return security_group_id, key_name, key_path


def _cleanup_ec2_environment(client, security_group_id, key_name, key_path):
    try:
        client.delete_security_group(GroupId=security_group_id)
        client.delete_key_pair(KeyName=key_name)
    except ClientError as e:
        print e

    os.remove(key_path)


def _create_security_group(client):
    response = client.describe_vpcs()
    default_vpc = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = client.create_security_group(
            GroupName="testinfra_%s" % str(uuid.uuid4()).replace('-', '_'),
            Description='TestInfra Temporary Group',
            VpcId=default_vpc
        )
        security_group_id = response['GroupId']

        client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [
                        {'CidrIp': '0.0.0.0/0'}
                    ]
                },
            ]
        )
    except ClientError as e:
        print e

    return security_group_id


def _create_ssh_keypair(client):
    try:
        response = client.create_key_pair(
            KeyName="testinfra_%s" % str(uuid.uuid4()).replace('-', '_')
        )
    except ClientError as e:
        print e

    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(response['KeyMaterial'])

    return response['KeyName'], path


def _setup_ssh_config(identity_file):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        tmp.write('Host *\n')
        tmp.write('  User %s\n' % SSH_USERNAME)
        tmp.write('  IdentityFile %s\n' % identity_file)
        tmp.write('  StrictHostKeyChecking no\n')

    return path
