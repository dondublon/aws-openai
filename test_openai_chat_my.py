import os

import requests

API_KEY = os.environ.get("BEDROCK_KEY")
modelId="amazon.nova-micro-v1:0"
modelId="openai.gpt-oss-20b-1:0"
modelId="arn:aws:bedrock:eu-north-1:519041483676:inference-profile/eu.amazon.nova-2-lite-v1:0"
modelId="arn:aws:bedrock:eu-north-1:519041483676:inference-profile/eu.amazon.nova-micro-v1:0"
modelId="amazon.titan-embed-text-v2:0"
import boto3

client = boto3.client(
    "bedrock-runtime",
    region_name="eu-north-1"
)

response = client.converse(
    modelId="arn:aws:bedrock:eu-north-1:519041483676:inference-profile/eu.amazon.nova-micro-v1:0",
    messages=[
        {
            "role": "user",
            "content": [
                {"text": "test connection"}
            ]
        }
    ]
)

print(response["output"]["message"]["content"][0]["text"])