import boto3

def create_vpc_resources():
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    ec2_client = boto3.client('ec2', region_name='us-east-1')

    try:
        # Create VPC
        vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
        vpc.create_tags(Tags=[{"Key": "Name", "Value": "Bar-Vpc"}])
        vpc.wait_until_available()

        # Enable DNS support and DNS hostnames
        ec2_client.modify_vpc_attribute(VpcId=vpc.id, EnableDnsSupport={'Value': True})
        ec2_client.modify_vpc_attribute(VpcId=vpc.id, EnableDnsHostnames={'Value': True})

        # Create and attach internet gateway
        internet_gateway = ec2.create_internet_gateway()
        vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)

        # Create public route table and route
        public_route_table = ec2.create_route_table(VpcId=vpc.id)
        public_route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internet_gateway.id)

        # Create public subnet and associate with route table and allocate public ip
        public_subnet = ec2.create_subnet(
            CidrBlock='10.0.1.0/24',
            VpcId=vpc.id,
            AvailabilityZone='us-east-1a'  # Specify the Availability Zone
        )
        public_route_table.associate_with_subnet(SubnetId=public_subnet.id)
        public_subnet.create_tags(Tags=[{"Key": "Name", "Value": "bar-public-sub"}])
        ec2_client.modify_subnet_attribute(SubnetId=public_subnet.id, MapPublicIpOnLaunch={'Value': True})

        # Create private subnet (No internet access)
        private_subnet = ec2.create_subnet(CidrBlock='10.0.2.0/24', VpcId=vpc.id)
        private_subnet.create_tags(Tags=[{"Key": "Name", "Value": "bar-private-sub"}])

        # Create security group
        security_group = ec2.create_security_group(GroupName='SSH-ONLY', Description='Allow SSH traffic', VpcId=vpc.id)
        security_group.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)

        print("VPC, subnets, route table, and security group created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_vpc_resources()
