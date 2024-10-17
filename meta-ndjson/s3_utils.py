import boto3

def connect_s3():
	return boto3.client('s3')

def get_file_data_from_s3(s3, bucket_name, prefix):
	paginator = s3.get_paginator('list_objects_v2')
	pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
	file_data = []
	for page in pages:
		for obj in page['Contents']:
				
				path = obj['Key']
				if  path.endswith('/'):
					continue
				mod_time = obj['LastModified']
				file_data.append({
					'Path': path,
					'bucket': bucket_name,
					'ModTime': mod_time.isoformat()
				})
	return file_data
