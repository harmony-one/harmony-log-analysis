# Validator and Delegator Analysis for mainnet
Get validators and delegators' information, including all the info on [staking dashboard](https://staking.harmony.one/validators) like profile, performance, general info, and also some other basic information. 

The following instruction assumes you are running on [Analytics VM](http://analytics.hmny.io/tree/harmony-log-analysis/projects/staking_dashboard) If you want to run locally, please skip the following instructions and go to [RUN LOCALLY](https://github.com/harmony-one/harmony-log-analysis/tree/master/projects/staking_dashboard#run-locally)

## Goal
- Track validator/delegator's performance, catch any abnormal activities (too frequent transactions, abnormal balance)
- Help validator troublesheet the reasons why they are not elected, filter those who have high uptime but still not get elected.
- Marketing purpose, manage the general info about our validators, email, website.

## Validator Key Information
To get name, ONE address, apr, total-stake, self-stake, fees, uptime, epos-status and boot status for
 validators. It's currently updating every epoch.

### Commands
Open a terminal, and run command: `python3 [path/to/script]/mainnet_validator_stats.py`

### Output
- [google spreadsheet tab validator-tracker](https://docs.google.com/spreadsheets/d/1AyYHWSkKOCzMY0ZvoT049DapIDvkEhpnfbA1WidJm3o/edit?usp=sharing)
- [google spreadsheet tab filter-validator-tracker](https://docs.google.com/spreadsheets/d/1AyYHWSkKOCzMY0ZvoT049DapIDvkEhpnfbA1WidJm3o/edit?usp=sharing)

## Validator Dashboard Information
To get min-self-delegation, max-total-delegation, rate, max-rate, max-change-rate, name, identity, website, security-contact, details, creation-height, address, self-stake, total-stake, active-nodes, elected-nodes, uptime-percentage, apr, lifetime-reward-accumulated, all the information on dashboard. It's currently manual updated.

### Commands
Open a terminal, and run command: `python3 [path/to/script]/mainnet_validator_dashboard.py`

### Output
`./csv/validator_info_mainnet.csv`

## Delegator Key Information
To get address, current-reward, total-stake, balance, staking-transaction-count, normal-transaction-count for delegators. It's currently updating every day.

### Commands
Open a terminal, and run command: `python3 [path/to/script]/mainnet_delegator_stats.py`

### Output
[google spreadsheet tab delegator-tracker](https://docs.google.com/spreadsheets/d/1AyYHWSkKOCzMY0ZvoT049DapIDvkEhpnfbA1WidJm3o/edit?usp=sharing)

## Run locally
If you want to run locally, you need to install the required packages and download the script, remember to download the script with `local` keyword. Take validator key information for example.

### Requirements
`python3 -m pip install requests pandas numpy`
If you meet permission denied errors, try using `python3 -m pip install --user requests pandas numpy`

### Download newest script
`curl -O https://raw.githubusercontent.com/harmony-one/harmony-log-analysis/master/notebooks/staking_dashboard/mainnet_validator_stats_local.py`

### Commands
Run command: `python3 mainnet_validator_stats_local.py`

### Output
- `./csv/mainnet_validator/*_validator.csv`
- `./csv/mainnet_validator/*_filter_validator.csv` (the validator who has more than 80% uptime but not eligible to be elcted) 
