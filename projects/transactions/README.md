# Transactions
This project provides the notebook to check transaction activity level for mainnet. 

## Daily Data
### Commands
- Run [data processing script](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/transactions/notebooks/data_processing_04_19.ipynb)
- Run [data visualization script](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/transactions/notebooks/2020_04_19_transactions_mainnet.ipynb)

### Result 
Date: 2020/4/19 00:00:00 - 2020/4/20 00:00:00 UTC
- Transactions 132
- Staking transactions 3446
- [Visualization](https://harmony-one.github.io/harmony-log-analysis/notebooks/transactions/2020_04_19_transactions_mainnet)(features aggregated in 5 minutes)

## Accumulated Data
### Commands
- Run `python3 TransactionCount.py --endpoints [ENDPOINTS] --network mainnet` collect txs counts for each shard
- Run `python3 read_count.py --network mainnet` calculate total counts and upload to google spreadsheet
- Run [data visualization script](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/transactions/notebooks/visualization_transactions.ipynb) for visualization

### Result
Date: 2019/06/28 - 2020/05/06
[Visualization](https://harmony-one.github.io/harmony-log-analysis/notebooks/transactions/mainnet_2020_05_06.html)
