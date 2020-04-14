# Staking Dashboard Analysis
Get validators or delegators' information on staking dashboard: https://staking.harmony.one/validators

## Requirements
`python3 -m pip install requests pandas numpy`

## Output
`./csv/*`

## Validator Info
To get information including name, address, website, details, security-contact, identity, epos-status, currently-in-committee, apr, delegator-num, bls-key-num, current-epoch-signed, current-epoch-signing-percentage, current-epoch-to-sign, num-beacon-blocks-until-next-epoch, reward, uptime-percentage

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/notebooks/staking_dashboard/validators-info.py`

### Commands
Run command: default is to get all the information of validators and save it to a csv file and stored in `./csv/validator_info.csv`: `python3 validators-info.py`

To change the output file name: `python3 validators-info.py --output_file new_name`

To print the statistics of epos-status: `python3 validtaors-info.py --epos_status`

To print the new validators who are not in the `harmony.one/keys`: `python3 validators-info.py --new_validators`

To print both information: `python3 validators-info.py --all`

## Delegator Info
To get the accumulated rewards(after claiming), balance, and stakes for pure delegators.

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/notebooks/staking_dashboard/delegator_info.py`

### Commands
Run command: `python3 delegator_info.py`


