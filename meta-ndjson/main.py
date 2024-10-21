import argparse
from s3_utils import *
from file_utils import *
import json

def parse_arguments():
	parser = argparse.ArgumentParser(description='Process some files.')
	parser.add_argument('--sample_family', type=str, required=True, help='Path to sample_family.csv')
	parser.add_argument('--s3_bucket_raw', type=str, required=True, help='S3 bucket name')
	parser.add_argument('--s3_bucket_prod', type=str, required=True, help='S3 bucket name')
	parser.add_argument('--studies_name', type=str, required=True, help='S3 prefix to list files')
	parser.add_argument('--info_workflows', type=str, required=True, help='S3 prefix to list files')
	parser.add_argument('--output_filename', type=str, required=True, help='S3 prefix to list files')
	return parser.parse_args()



def main():
	args = parse_arguments()
	
	family_samples = read_sample_family(args.sample_family)
	info_workflows = read_yaml(args.info_workflows)

	
			
	# Connect to S3
	s3 = connect_s3()

	# Load raw data
	studies_raw_name = f"" 	+ args.studies_name + "/"
	file_data = get_file_data_from_s3(s3, args.s3_bucket_raw,studies_raw_name)


	# Load import data
	studies_import_name = f"studies/" 	+ args.studies_name + "/"
	file_data_import = get_file_data_from_s3(s3, args.s3_bucket_prod,studies_import_name)
	file_data.extend(file_data_import)


	# Construct metadata entries
	metadata_entries = {}
	metadata_entries["submissionSchema"] =  info_workflows['submissionSchema']

	
	analysis = []
	for family_id, sample_ids  in family_samples.items():
		for sample_id, aliquot_id , relation_to_proband , dataset_id , studies_id , to_exlude in sample_ids:
			if to_exlude == True :
				continue

			files = {}
			# Vep annotaed only for proband
			if ("proband") in relation_to_proband :
				snv_file = find_files(file_data, sample_id, family_id, info_workflows['analyses']['files']['snv'])
				snv_idx = find_files(file_data, sample_id, family_id, info_workflows['analyses']['files']['snv_idx'])
				if snv_file:
					files["snv"] = snv_file
				if snv_idx:
					files["snv_idx"] = snv_idx

			for file_type, patterns in info_workflows['analyses']['files'].items():
				if file_type not in ["snv", "snv_idx"]:  # Skip snv and snv_idx as they are handled separately
					found_files = find_files(file_data, sample_id, family_id, patterns)
					if found_files:
						files[file_type] = found_files


			entry = {
				"ldmSampleId": sample_id,
				"labAliquotId": aliquot_id,
				"familyID": family_id,
				"files": {key: value for key, value in files.items() if value is not None},
				"specimenType": info_workflows['analyses']['specimenType'],
				"sampleType": info_workflows['analyses']['sampleType']
				
			}
			if dataset_id:
				entry["dataset"] = dataset_id

			analysis.append(entry)


	# Add analysis information if not null
	if analysis:
		metadata_entries["analysis"] = analysis

	# Add experiment information if not null
	experiment_info = {key: value for key, value in info_workflows['experiment'].items() if value is not None}
	if experiment_info:
		metadata_entries["experiment"] = experiment_info
		

	# Add workflow information if not null
	workflow_info = {key: value for key, value in info_workflows['workflow'].items() if value is not None}
	if workflow_info:
		metadata_entries["workflow"] = workflow_info
		
		

	# Write the metadata entries to metadata.json
	with open(args.output_filename, 'w') as output_file:
		json.dump(metadata_entries, output_file, indent=4)

if __name__ == "__main__":
	main()