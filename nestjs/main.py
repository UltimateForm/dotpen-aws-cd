from aws_cdk import (
    Stack,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
    aws_ssm as ssm,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    CfnParameter,
)
import os
from constructs import Construct


class NestJsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        neo4j_user = ssm.StringParameter.value_from_lookup(
            self, f"/{construct_id}/neo4j-username"
        )
        neo4j_db = ssm.StringParameter.value_from_lookup(
            self, f"/{construct_id}/neo4j-database"
        )
        neo4j_password = ssm.StringParameter.from_string_parameter_name(
            self, "NEO4J PASSWORD", f"/{construct_id}/neo4j-password"
        ).string_value
        jwt_secret = ssm.StringParameter.from_string_parameter_name(
            self, "JWT SECRET", f"/{construct_id}/jwt-secret"
        ).string_value
        neo4j_uri = ssm.StringParameter.value_from_lookup(
            self, f"/{construct_id}/neo4j-uri"
        )
        account_id = os.environ["CDK_DEFAULT_ACCOUNT"]
        region = os.environ["CDK_DEFAULT_REGION"]
        repo = ecr.Repository.from_repository_attributes(
            self,
            id="Repo",
            repository_arn=f"arn:aws:ecr:{region}:{account_id}:repository/{construct_id}",
            repository_name=construct_id,
        )
        image_tag = CfnParameter(self, "imageTag", type="String")
        cluster = ecs.Cluster(self, "MainApiCluster")
        cluster.add_capacity(
            "MainApiAutoScalingGroup1",
            instance_type=ec2.InstanceType("t2.micro"),
            max_capacity=1,
        )
        cluster.add_capacity(
            "MainApiAutoScalingGroup2",
            instance_type=ec2.InstanceType("t2.micro"),
            max_capacity=1,
        )
        ecs_patterns.ApplicationLoadBalancedEc2Service(
            self,
            "MainApiEc2Service",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=1024,
            memory_reservation_mib=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                    repo, image_tag.value_as_string
                ),
                environment={
                    "NEO4J_USERNAME": neo4j_user,
                    "NEO4J_DATABASE": neo4j_db,
                    "NEO4J_PASSWORD": neo4j_password,
                    "NEO4J_URI": neo4j_uri,
                    "JWT_SECRET": jwt_secret,
                },
                container_port=3000,
            ),
            desired_count=1,
        )
