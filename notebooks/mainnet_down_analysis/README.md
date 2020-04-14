# Mainnet Crash Analysis
On March 30th and March 31st (UTC), our mainnet got attacked and all four shards are down. This project provides some insights on the p2p level message, bootnode and rx-overrun error during the attack. Also, the project analyzed the stress testnet when seb is doing txs spamming. 

- [Bootnode analysis](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/100.26.90.187-bootnode.ipynb)

- Mainnet shard 3 leader (the only one has overrun error)
	- [Block message](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/34.220.68.43_shard3_leader_block_message.ipynb)
	- [Overrun error](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/34.220.68.43_shard3_leader_overrun.ipynb)

- Mainnet shard 0 leader
	- [Block message](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/13.229.205.39_shard0_leader_block_message.ipynb)

- Stress network 04-03
	- [Shard0 leader](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/18.237.207.112-stn-04-03.ipynb)

- Stress network 04-06
	- [Validator](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/52.27.148.243-stn-04-06.ipynb)
	- [Shard0 leader](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/54.202.135.52-stn-04-06.ipynb)
	- [Shard1 leader](https://github.com/harmony-one/harmony-log-analysis/blob/master/notebooks/mainnet_down_analysis/54.177.252.88-stn-04-06.ipynb)

