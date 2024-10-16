import argparse
from s3_utils import connect_s3, get_file_data_from_s3
from file_utils import read_sample_family, read_yaml, read_ids_to_exclude, find_files
import json

def parse_arguments():
	parser = argparse.ArgumentParser(description='Process some files.')
	parser.add_argument('--sample_family', type=str, required=True, help='Path to sample_family.csv')
	parser.add_argument('--id_to_exclude', type=str, required=True, help='Path to ID_TO_EXCLUDE.tsv')
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
	ids_to_exclude = read_ids_to_exclude(args.id_to_exclude)
	
	
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
	metadata_entries = []
	for family_id, sample_ids  in family_samples.items():
		for sample_id, aliquot_id , relation_to_proband in sample_ids:
			if sample_id in ids_to_exclude:
				continue
			
			# Vep annotaed only for proband
			if ("proband") in relation_to_proband :
				snv_file  =	find_files(file_data, sample_id, family_id, [r'vep.vcf.gz'])
				snv_idx  =	find_files(file_data, sample_id, family_id, [r'vep.vcf.gz.tbi'])
			else:
				snv_file  =	None
				snv_idx  =	None
			
			gvcf_file = find_files(file_data, sample_id, family_id, [r'.g.vcf.gz',r'.gvcf.gz'])
			gvcf_idx = find_files(file_data, sample_id, family_id, [r'.g.vcf.gz.tbi',r'.gvcf.gz.tbi'])
			cram_file = find_files(file_data, sample_id, family_id, [r'.cram'])
			crai_file = find_files(file_data, sample_id, family_id, [r'.crai'])
			fastq1 = find_files(file_data, sample_id, family_id, [r'R1.*\.fastq.gz'])
			fastq2 = find_files(file_data, sample_id, family_id, [r'R2.*\.fastq.gz'])
			cnv = find_files(file_data, sample_id, family_id, [r'.cnv.vcf.gz'])
			cnv_idx = find_files(file_data, sample_id, family_id, [r'.cnv.vcf.gz.tbi'])
			sv = find_files(file_data, sample_id, family_id, [r'.sv.vcf.gz'])
			sv_idx = find_files(file_data, sample_id, family_id, [r'.sv.vcf.gz.idx'])
			bam = find_files(file_data, sample_id, family_id, [r'.bam'])
			bai = find_files(file_data, sample_id, family_id, [r'.bai'])
			

			entry = {
				"ldmSampleId": sample_id,
				"labAliquotId": aliquot_id,
				"familyID": family_id,
				
				"files": {
					"snv"		: snv_file	if snv_file	 is not None else None,
					"snv_idx"	: snv_idx	if snv_idx	 is not None else None,
					"gvcf"		: gvcf_file if gvcf_file is not None else None,
					"gvcf_idx"	: gvcf_idx if gvcf_idx is not None else None,
					"cram"		: cram_file if cram_file is not None else None,
					"crai"		: crai_file if crai_file is not None else None,
					"bam"		: bam if bam is not None else None,
					"bai"		: bai if bai is not None else None,
					"fastq1"	: fastq1 if fastq1 is not None else None,
					"fastq2"	: fastq2 if fastq2 is not None else None,
					"cnv"		: cnv if cnv is not None else None,
					"cnv_idx"	: cnv_idx if cnv_idx is not None else None,
					"sv" 		: sv if sv is not None else None,
					"sv_idx" 	: sv_idx if sv_idx is not None else None
				},
				"dataset": info_workflows['analyses']['dataset'],
				"specimenType" : info_workflows['analyses']['specimenType'],
				"sampleType" : info_workflows['analyses']['sampleType']
			}
			metadata_entries.append(entry)

	#Add fsample and files to metadata
	info_workflows['analyses'] = metadata_entries

	# Write the metadata entries to metadata.json
	with open(args.output_filename, 'w') as file:
		json.dump(info_workflows, file, indent=4)

if __name__ == "__main__":
	main()