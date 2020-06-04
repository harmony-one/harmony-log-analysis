# Foundational Node Tracker
This project provides info for foundational nodes before our mainnet enters into open-staking period on May 16th 2020, including signing percentage, accumulated earned rewards, balance and txs history.

## Requirements
`python3 -m pip install requests, pandas, pyhmy==20.5.3`

## Signing Percentage Calculation
- get signer every block: 
	- Create a new tmux session using `tmux new -s block_signer`
	- Run the script: `python3 block_signers.py --endpoints [ENDPOINT] --network mainnet`
- get committee member every epoch:
	- Create a new tmux session using `tmux new -s committee`
	- Run the script: `python3 get_committee.py --endpoints [ENDPOINT] --network mainnet`
- get signing percentage: `python3 get_signing_percentage.py`

## Accumulated rewards earned
### Every FN nodes
balance + ONE-sent - ONE-received + total-stake (during pre-staking) + txs-fee + staking-txs-fee 

#### Command
Run `python3 balance_tracker.py`

#### Result 
[google spreadsheet FN-tracker](https://monitor.hmny.io/fn_earnings)

### Total rewards
sum of block-number for each shard when enter into open-staking

#### Command
- First get the block-number in shard 0 when we enter into epoch 186, `block-number-shard-0 = mainnetEpochBlock1 + 185*blocksPerEpoch`
- Run `python3 get_open_staking_block_number.py` to get the time when we enter into open-staking and get the block number in non-beacon shards which is closest to the time. 
- Calculate: `sum(block-number-in-all-shards) * 24`

#### Result
We burned [319237512 tokens](https://twitter.com/harmonyprotocol/status/1265793826251108353)
