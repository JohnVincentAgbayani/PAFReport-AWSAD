import boto3
import json
import os

target_env = "Deltekdev"

for item in os.listdir():
	if target_env in item:
		s3_client = boto3.client('s3')
		s3_client.upload_file(item, "infrasre-adreports-main", f'{target_env}/{item}')