import boto3
import os

def deploy_lambda():
    region = "eu-central-1"
    function_name = "rss-lambda-taz"
    role_arn = os.getenv("LAMBDA_ROLE_ARN")
    image_uri = os.getenv("ECR_IMAGE_URI")

    if not role_arn or not image_uri:
        print("Error: LAMBDA_ROLE_ARN and ECR_IMAGE_URI must be set.")
        return

    client = boto3.client("lambda", region_name=region)

    try:
        # Check if function exists
        client.get_function(FunctionName=function_name)
        print(f"Updating existing function {function_name}...")
        client.update_function_code(
            FunctionName=function_name,
            ImageUri=image_uri
        )
    except client.exceptions.ResourceNotFoundException:
        print(f"Creating new function {function_name}...")
        client.create_function(
            FunctionName=function_name,
            Role=role_arn,
            Code={'ImageUri': image_uri},
            PackageType='Image'
        )

    print("Lambda deployment successful.")

if __name__ == "__main__":
    deploy_lambda()
