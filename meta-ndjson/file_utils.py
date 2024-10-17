import csv
import yaml
from datetime import datetime
import re

def read_sample_family(file_path):
	family_samples = {}
	with open(file_path, 'r') as csvfile:
		reader = csv.reader(csvfile)
		next(reader)  # Skip the header line
		for row in reader:
			sample_id, aliquot_id, family_id , relation_to_proband = row
			if family_id not in family_samples:
				family_samples[family_id] = []
			family_samples[family_id].append((sample_id, aliquot_id,relation_to_proband))
	return family_samples

def read_yaml(file_path):
	with open(file_path, 'r') as file:
		return yaml.safe_load(file)

def read_ids_to_exclude(file_path):
	with open(file_path, 'r') as file:
		return set(line.strip() for line in file)
	
def find_files(file_data, sampleID, familyID, patterns):
	most_recent_file = None
	most_recent_version = None
	
	for file in file_data:
		path = file['Path']
		match = re.search(r'/dataset_v(\d+)/', path)
		if match:
			version = int(match.group(1))
		else :
			version = None

		mod_time = datetime.fromisoformat(file['ModTime'].replace('Z', '+00:00'))

		if (sampleID in path or re.sub(r'[a-zA-Z]', '', sampleID) in path or familyID in path) :
			for pattern in patterns:
				regex = re.compile(pattern + r'$' ,flags=re.IGNORECASE)
				if re.search(regex, path):
					if most_recent_version is None or version > most_recent_version:
						most_recent_file = f"s3://" + file['bucket']+ "/" + path
						most_recent_version = version
					break
	  
	return most_recent_file if most_recent_file is not None else None