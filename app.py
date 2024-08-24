from nestjs.main import NestJsStack
import aws_cdk as cdk
import argparse
import os

parser = argparse.ArgumentParser(description="CDK PYTHON CLI TOOL")
parser.add_argument("stack", choices=["nestjs"])
parser.add_argument("name", help="name for the stack")

args = parser.parse_args()
stack_type = args.stack
stack_name = args.name

app = cdk.App()

if stack_type == "nestjs":
    NestJsStack(
        app,
        stack_name,
        env={
            "account": os.environ["CDK_DEFAULT_ACCOUNT"],
            "region": os.environ["CDK_DEFAULT_REGION"],
        },
    )

app.synth()
