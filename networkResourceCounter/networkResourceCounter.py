import json
import boto3
import re
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# environment variables
vpc = os.environ['TARGET_VPC']
cw_namespace = os.environ['CW_NAMESPACE']


def get_resource_counts(vpc):

    logger.info(f"funct:: get_resource_counts started for VPC: {vpc}... ")

    # counter defninitions
    nlb_eni_count=0
    vpc_endpoint_eni_count=0
    vpc_lambda_eni_count=0
    ip_count=0
    prefix_delegation_count=0

    # ec2 client with paginator to go through in-use ENIs in specified VPC ID
    ec2_client = boto3.client('ec2')

    paginator = ec2_client.get_paginator('describe_network_interfaces')
    pagination_args = {
        'Filters': [
            {
                'Name': 'vpc-id',
                'Values': [vpc]
            },
            {
                'Name': 'status',
                'Values': ['in-use']
            }

        ],
        'MaxResults': 1000
    }
    page_iterator = paginator.paginate(**pagination_args)


    for page in page_iterator:

        # Count IPs on each ENI
        for interface in page['NetworkInterfaces']:
            eni_ip_count = len(interface['PrivateIpAddresses']) + len(interface['Ipv6Addresses'])
            prefix_delegation_count += len(interface.get('Ipv4Prefixes',[])) + len(interface.get('Ipv6Prefixes',[]))
            ip_count += eni_ip_count

            # Counting hyperplane resources
            if interface['InterfaceType'] != 'interface':

                ip_count += 5 * eni_ip_count

                if re.search('^ELB net/', interface['Description']):
                    nlb_eni_count += 1
                elif re.search('^VPC Endpoint Interface', interface['Description']):
                    vpc_endpoint_eni_count += 1
                elif re.search('^AWS Lambda', interface['Description']):
                    vpc_lambda_eni_count += 1


    logger.info(f"funct:: get_resource_counts: Number of IP addreses: {ip_count}")
    logger.info(f"funct:: get_resource_counts: Number prefix delegations: {prefix_delegation_count}")
    logger.info(f"funct:: get_resource_counts: Number NLB ENIs: {nlb_eni_count}")
    logger.info(f"funct:: get_resource_counts: Number of VPC Endpoint ENIs: {vpc_endpoint_eni_count}")
    logger.info(f"funct:: get_resource_counts: Number of Lambda ENIs: {vpc_lambda_eni_count}")
    logger.info(f"funct:: get_resource_counts finished...")

    return {
            'IPaddressCount': ip_count,
            'PrefixDelegationCount': prefix_delegation_count,
            'NLBeniCount': nlb_eni_count,
            'VPCendpointEniCount': vpc_endpoint_eni_count,
            'LambdaEniCount': vpc_lambda_eni_count
            }

def publish_to_cw(vpc, cw_namespace, values):

    logger.info("funct:: publish_to_cw started... ")

    # CloudWatch client to push the counters as metrics
    cw_client = boto3.client('cloudwatch')

    # Create the metrics
    metric_data = []

    for item in values:
        metric = {
            'MetricName': item,
            'Dimensions': [
                {
                    'Name': 'vpc id',
                    'Value': vpc
                },
            ],
            'Value': values[item],
            'Unit': 'Count',
            }
        metric_data.append(metric)

    logger.info("funct:: publish_to_cw: pushing metrics to CloudWatch")

    cw_client.put_metric_data(
        Namespace=cw_namespace,
        MetricData=metric_data
        )

    logger.info("funct:: publish_to_cw finished...")

def lambda_handler(event, context):

    # Count Resources
    counts = get_resource_counts(vpc)

    # Publish values as CloudWatch Metric
    publish_to_cw(vpc, cw_namespace, counts)
