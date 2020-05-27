# Foundational Node Tracker
This project provides info for foundational nodes before our mainnet enters into open-staking period on May 16th 2020, including signing percentage, accumulated earned rewards, balance and txs history.

## Requirements
`python3 -m pip install requests, pandas, pyhmy==20.5.5`

## Signing Percentage Calculation
- get signer every block: 
	- Create a new tmux session using `tmux new -s block_signer`
	- Run the script: `python3 block_signers.py --endpoints [ENDPOINT] --network mainnet`
- get committee member every epoch:
	- Create a new tmux session using `tmux new -s committee`
	- Run the script: `python3 get_committee.py --endpoints [ENDPOINT] --network mainnet`
- get signing percentage: `python3 get_signing_percentage.py`

## Accumulated rewards earned
### Method1
balance + ONE-sent - ONE-received + total-stake (during pre-staking) 

#### Command
Run `python3 balance_tracker.py`

#### Result 
[google spreadsheet FN-tracker](https://docs.google.com/spreadsheets/d/1AyYHWSkKOCzMY0ZvoT049DapIDvkEhpnfbA1WidJm3o/edit?usp=sharing)

### Method2
sum of block-number for each shard when enter into open-staking

#### Command
Run [jupyter notebook](https://github.com/harmony-one/harmony-log-analysis/tree/master/projects/FN_tracker/notebooks/get_block_number_open_staking.ipynb)

#### Result
shard 0:`3375104`, time: `2020_05_16_15:08:52 UTC` (`2020_05_16_08:08:52 PST`)

shard 1:`3286736`, time: `2020_05_16_15:08:53 UTC` (`2020_05_16_08:08:53 PST`)

shard 2:`3326152`, time: `2020_05_16_15:08:56 UTC` (`2020_05_16_08:08:56 PST`)

shard 3:`3313571`, time: `2020_05_16_15:08:53 UTC` (`2020_05_16_08:08:53 PST`)
