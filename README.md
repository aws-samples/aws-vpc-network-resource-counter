# AWS Network Resource Counter for Amazon VPC

## About
This project is intended to help with tracking networking resources in a single Amazon VPC. It will create an AWS Lambda function that will count specific network resources and will create CloudWatch metric for each measurement. The measurements are published at an interval of your choice.

## Counted resources and their metrics:
When you run this code you can select the CloudWatch metric namespace under which the metrics will be tracked.

Below are the generated CloudWatch metrics and resources they are tracking:

* **IPaddressCount** - Total number of IP addresses in a VPC (combined IPv4 and IPv6 addresses)
* **PrefixDelegationCount** - Total number of prefix delegations in a VPC. You can read more about prefix delegation feature [here](https://aws.amazon.com/about-aws/whats-new/2021/07/amazon-virtual-private-cloud-vpc-customers-can-assign-ip-prefixes-ec2-instances/)
* **NLBeniCount** - Total number of Network Load Balancer (NLB) Elastic Network Interfaces (ENI). The default quotas for NLB ENIs are listed [here](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-limits.html)
* **VPCendpointEniCount** - Total number of VPC Interface Endpoints (powered by PrivateLink). The default quotas for VPC Endpoints are covered [here](https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-endpoints)
* **LambdaEniCount** - Total number of VPC Elastic Network Interfaces used by AWS Lambda. AWS Lambda quotas are covered [here](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)

Once you have these metrics in CloudWatch you can easily create alarms to let you know that a certain value is getting close to the offered quota. You can find out how to create a CloudWatch alarm from a metric [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create_alarm_metric_graph.html)


## Deployment
The AWS Lambda code required for this sample to run in your AWS account is in the networkResourceCounter folder. If you want to manually deploy it in your account you'll need to setup appropriate permissions for your Lambda to be able to describe ENIs and publish metrics to CloudWatch. You will also need to setup a schedule based CloudWatch event to run it.

If you prefer to use SAM CLI to automate the deployment process you can follow the steps below.

### Prerequisites for SAM CLI
To streamline the setup process, this project is using AWS Serverless Application Model (AWS SAM). All the components and their interactions are defined in the AWS SAM template that can be easily deployed into your AWS account.

To use the AWS SAM Command Line Interface (CLI) and complete this project, you need the following tools.

* AWS SAM CLI – [Install the AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3.8](https://www.python.org/downloads/) installed - without it SAM BUILD will not work


### SAM Deployment Walkthrough
1. Confirm you completed all prerequisites listed above
2. Clone or Download this repository into your local machine
3. Follow instructions below to build a sam project.

To build project:
```
sam build
```

To deploy project:
```
sam deploy --guided
```

You will be prompted for parameter values. Below table explains their purpose.


| Property                | Description           | Value Format Example  |
| ----------------------- |---------------------| :--------------:|
| **Stack Name**          | The name of the stack to deploy to CloudFormation. | give it a unique name          |
| **AWS Region**| AWS Region where you deploy your app. This must be the same region where your VPC is hosted and where CloudWatch metrics will be published into | us-west-x |
| **VPC ID** | The ID of the VPC you want to monitor resources for. Make sure it's in the correct AWS Region | vpc-123|
| **CloudWatch Namespace** | The custom namespace to group your CloudWatch metrics | CUSTOM/VPC_Network_Resource_Tracker |
| **Schedule** | Provide a value in minutes on how often you want the counter to run. Supported values from 5 to 1440 | 30 |




## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
