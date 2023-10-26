import json
import pandas as pd
from datetime import datetime

target_env = "Costpoint"

with open("stdout.txt", encoding="utf8", errors='ignore') as f:
		stdout_str = f.read()

stdout_split = stdout_str.split("\n")

base_df = pd.DataFrame(columns = ['USERNAME', 'EMAIL', 'EMPLOYEEID'])

print(f'\nConverting AD Report for {target_env} to CSV\n')
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
				print(append_df)

target_date = str(datetime.today().strftime('%Y-%m-%d'))
target_filename = f'{target_env}-ADreport-{target_date}.csv'
base_df.to_csv(str(target_filename), index=False)  
