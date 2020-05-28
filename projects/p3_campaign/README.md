# P3 Campaign Reward Calculation
This project records how we calculate the rewards validator/delegator earned during P3 campaign. The result is updated on the [google sheet](https://docs.google.com/spreadsheets/d/1Xgu4Kl3dl3gWDcJVXf3rvlIGav4mVPM5bILshkAowTk/edit?usp=sharing)

## Delegator Campaign
The campaign starts at April 30th, and ends at May 8th 10 AM PST. The rewards are 100% rewards earned from all deleagtions. 

### Equation
Reward = (Current balance + Staked amount + Unclaimed Rewards + Pending undelegation amount) - (Net Value of transfers) 

### Steps
 The detailed steps are as follows:
1. Get all account balances at last block
2. Get all account delegations at last block
3. Get list of all pending undelegations at last block
4. Get list of unclaimed rewards at last block
5. Get net value & number of all regular transactions to & from the account 

### Commands
- To get staked amount, unclaimed rewards and pending undelegations, run `python3 delegator_info_shard_0.py` in shard 0 locally with P3 database. 
- To get balance and net values of transfers, run `python3 delegator_info_shard_{SHAED}.py` for every shard locally.
- To get the last block for each shard when the campaign ends, run `python3 getBlockNumber.py`

Last Block: Shard 0: `88514`, Shard 1: `94941`, Shard 2: `95172`, Shard 3: `94857`

