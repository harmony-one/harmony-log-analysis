# Jenkins Job
During the deployment of Open Staking Network multiple releases have been performed. This project is to get the historical validator node release info from Jenkin's json api, which creats an easy to read table for harmony team to check.

## Requirements
`python3 -m pip install requests pandas`

## Download newest scripts
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/notebooks/jenkins/jenkins.py`

## Commands
Run command: `python3 jenkins.py` Output file will be saved in `./csv` directory

## Output
`./csv/*` 
