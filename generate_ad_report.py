import pandas as pd
import boto3
import json
import time

from datetime import datetime, timedelta	

def main():
	#RAW REPORT GENERATION

	ssm_file = open("get_ad_ssm.json")
	ssm_json = ssm_file.read()

	env_file = open("temp_env.txt")
	target_environment = env_file.read()
	target_env = target_environment.replace("\n","")

	instance_ids = {
		"Deltekdev":"i-04d0e953afe07b3a3",
		"DCO":"i-0fe3ff3ff41c18b17",
		"Costpoint":"i-0e82a12d1ef934425",
		"Flexplus":"i-0f2717bceb18eea6f",
		"GlobalOSS":"i-04b225ae477c52288",
		"Engdeltek":"i-0667aa10a44eafc7c",
	}

	ssm_doc_name = 'generate-paf-ad-report'
	ssm_client = boto3.client('ssm', region_name="us-east-1")
	target_instance = instance_ids[target_env]
	target_bucket = f'infrasre-adreport-raw-{target_env.lower()}'

	ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

	print(f'\nGenrating AD Report for {target_env}\n')
	ssm_run_response = ssm_client.send_command(InstanceIds = [target_instance], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120, OutputS3BucketName=target_bucket)
	print(f'{ssm_run_response}\n')
	cmd_id = ssm_run_response['Command']['CommandId']

	time.sleep(2)
	ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_instance)
	while ssm_status_response['StatusDetails'] == "InProgress":
		print(f'SSM command {cmd_id} is still executing in {target_env}, pausing for 30s')
		time.sleep(30)
		ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_instance)

	ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)

	#S3 PROCESSING AND CONVERSION

	#get output from s3
	target_date = str(datetime.today().strftime('%Y-%m-%d-%H_%M'))
	target_filename = f'{target_env}-ADreport-{target_date}.csv'

	s3_client = boto3.client('s3')
	s3_client.download_file(target_bucket, target_filename, target_filename)

main()