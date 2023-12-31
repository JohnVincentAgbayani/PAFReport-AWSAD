import boto3
import json
import os

env_file = open("temp_env.txt")
target_environment = env_file.read()
target_env = target_environment.replace("\n","")

for item in os.listdir():
	if target_env in item:
		s3_client = boto3.client('s3')
		print(f'\nUploading AD Report for {target_env}\n')
		s3_client.upload_file(item, "infrasre-adreports-main", f'{target_env}/{item}')
		os.remove(item)