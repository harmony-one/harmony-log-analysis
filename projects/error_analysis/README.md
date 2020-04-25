# Error Analysis
Provide the classification of errors in four levels: debug, info, warn, error in network level or node level.

## Network level
Currently the analysis for network level is implemented on OSTN. 

### Commands
Run command: `python3 network_error_ostn.py` It will ask you to specify the date and upload time folder, then it will download all nodes logs from s3 bukcet, do data processing, run analysis, and upload to the github pages for review. There is a delay about github pages refresh, please check the link after several minutes.

Examples:
- [OSTN-04-14](https://harmony-one.github.io/harmony-log-analysis/notebooks/error_analysis/ostn/20_04_14.html)

## Node level
Currently the analysis for node level is implemented on mainnet. 

### Commands
Run command: `python3 single_node_error_mainnet.py`, it will ask you the date and the node you want to inquiry, then download the corresponding logs from s3 bucket, do data processing, run analysis, and upload to the github pages for review. There is a delay about github pages refresh, please check the link after several minutes.

Examples:
- [2020-04-20-3.112.219.248](https://harmony-one.github.io/harmony-log-analysis/notebooks/error_analysis/mainnet/3.112.219.248/2020-04-20)
