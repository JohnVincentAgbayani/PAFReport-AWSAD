import pandas as pd
import boto3
import json
import time

from datetime import datetime	

def main():
	ssm_file = open("get_ad_ssm.json")
	ssm_json = ssm_file.read()

	env_file = open("temp_env.txt")
	target_environment = env_file.read()
	target_environment = target_environment.replace("\n","")

	instance_ids = {
		"Deltekdev":"i-04d0e953afe07b3a3",
		"DCO":"i-04eb952554db2e110",
		"Costpoint":"i-84e48028",
		"Flexplus":"i-0f2717bceb18eea6f",
		"GlobalOSS":"i-04b225ae477c52288",
		"Engdeltek":"i-0667aa10a44eafc7c",
	}

	ssm_doc_name = 'generate-paf-ad-report'
	ssm_client = boto3.client('ssm', region_name="us-east-1")
	target_instance = instance_ids[target_env]
	target_bucket = f'infrasre-adreport-raw-{target_env.lower()}'

	ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

	ssm_run_response = ssm_client.send_command(InstanceIds = [target_instance], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120, OutputS3BucketName=target_bucket)
	print(ssm_run_response)
	cmd_id = ssm_run_response['Command']['CommandId']

	ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)

	#get output from s3
	time.sleep(10)
	s3_client = boto3.client('s3')
	s3_download_path = f'{cmd_id}/{target_instance}/awsrunPowerShellScript/RunADReport/stdout'

	s3_client.download_file(target_bucket, s3_download_path, "stdout.txt")

	#CONVERT OUTPUT TO READABLE CSV

	stdout_file = open("stdout.txt")
	stdout_str = stdout_file.read()
	stdout_split = stdout_str.split("\n")

	base_df = pd.DataFrame(columns = ['USERNAME', 'EMAIL', 'EMPLOYEEID'])

	for user_data in stdout_split:
		if "-" not in user_data and "SamAccountName" not in user_data:
			user_data_split = user_data.split(" ")
			user_data_split = list(filter(None, user_data_split))

			append_data = {"USERNAME":[""],"EMAIL":[""],"EMPLOYEEID":[""]}

			if len(user_data_split)>0:

				if len(user_data_split)==1:
					append_data['USERNAME'][0] = user_data_split[0]
				elif len(user_data_split)==2:
					append_data['USERNAME'][0] = user_data_split[0]

					if "@" in user_data_split[1]:
						append_data['EMAIL'][0] = user_data_split[1]
					else:
						append_data['EMPLOYEEID'][0] = user_data_split[1]
				elif len(user_data_split)==3:
					append_data = {"USERNAME":[user_data_split[0]],"EMAIL":[user_data_split[1]],"EMPLOYEEID":[user_data_split[2]]}

				if not append_data['USERNAME']=="":
					append_df = pd.DataFrame(append_data, columns = ['USERNAME', 'EMAIL', 'EMPLOYEEID'])
					base_df = pd.concat([base_df, append_df])

	target_date = str(datetime.today().strftime('%Y-%m-%d'))
	target_filename = f'{target_env}-ADreport-{target_date}.csv'
	base_df.to_csv(str(target_filename), index=False)  


main()