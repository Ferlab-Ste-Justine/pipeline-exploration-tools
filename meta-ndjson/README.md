# Meta NDJSON Exploration Tools

This repository contains tools for create .ndjson files .

## Table of Contents
- [Introduction](#introduction)
- [Usage](#usage)


## Introduction
The role of the script is to create a .ndsjon file containing the necessary information for the ETL. The script retrieves the file paths from S3 for each sample, selecting the most recent one based on its directory structure.



## Usage
Here are some basic commands to get you started:
```sh
python main.py --sample_family family_file.csv --id_to_exclude ID_TO_EXCLUDE.tsv --s3_bucket_raw 'name-of-raw-bucket' --s3_bucket_prod 'name-of-prod-bucket' --studies_name 'name-of-studie' --info_workflows info_workflow.yml --output_filename 'metadata_R-X.ndjson'
```

Input : 

 - family_file.csv must be in format : 
submitter_sample_id,submitter_participant_id,submitter_family_id,relationship_to_proband

 - ID_TO_EXCLUDE.tsv must be in format :
 sample1
 sample2
 sample3

 - info_workflow.yml is a yml file use as a temple for the metadata.ndjson. 


## Improvement

 - Improve code with best practices
 - Extract the files to retrieve and their associated regular expressions into a parameter file.