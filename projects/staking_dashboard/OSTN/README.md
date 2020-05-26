# Staking Dashboard Analysis
Get validators or delegators' information on staking dashboard for OSTN: https://staking.harmony.one/validators (current website is mainnet)

## Requirements
`python3 -m pip install requests pandas numpy`

If you meet permission denied errors, try using `python3 -m pip install --user requests pandas numpy`


## Validator Info
To get information including name, address, website, details, security-contact, identity, epos-status, currently-in-committee, apr, delegator-num, bls-key-num, current-epoch-signed, current-epoch-signing-percentage, current-epoch-to-sign, num-beacon-blocks-until-next-epoch, reward, uptime-percentage

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/projects/staking_dashboard/OSTN/validator_info.py`

### Commands
Run command: default is to get all the information of validators and save it to a csv file and stored in `./csv/validator_info.csv`: `python3 validator_info.py`

To change the output file name: `python3 validator_info.py --output_file new_name`

To print the statistics of epos-status: `python3 validator_info.py --epos_status`

To print the statistics of unique users' epos-status and duplicate validators' info: `python3 validator_info.py --epos_status_unique`

To print the new validators who are not in the `harmony.one/keys`: `python3 validator_info.py --new_validators`

To print both information: `python3 validator_info.py --all`

### Output
`./csv/*`

## Pure Delegator Info
To get the accumulated rewards(after claiming), balance, and stakes for pure delegators.

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/projects/staking_dashboard/OSTN/delegator_info.py`

### Commands
Run command: `python3 delegator_info.py`

### Output
`./csv/pure_delegator/*`

## All Delegator Info
To get the accumulated rewards(after claiming), balance, and stakes for all delegators (delegators + validators).

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/projects/staking_dashboard/OSTN/all_delegator_info.py`

### Commands
Run command: `python3 all_delegator_info.py`

### Output
`./csv/all_delegator/*`

## Transaction History 
To get the transaction history of one acoount

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/projects/staking_dashboard/OSTN/transaction_history.py`

### Commands
Run command: get all transaction history for a ONE account, with maximum 10000 reocrds and save it to a csv file and stored in `./csv/[NAME]_transaction.csv`: `python3 transaction_history.py --address [YOUR ONE ADDRESS] --name [YOUR NAME]`

### Output
`./csv/*`

