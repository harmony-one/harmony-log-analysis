# Processing time Analysis
This project analyzed how processing time changed with block height increases and delegation scaling. Also it visualized the processing time of 7 key economic activity.   

## Motivation
We noticed sometimes the processing the time increases when the block height increase, and it shows [stepped pattern](https://harmony-one.github.io/harmony-log-analysis/graphs/processing_time/OSTN_03_04/block_height/2_processing_time_vs_block_height.html) we would like to discover what features will casue the delay of processing time.

## Result
- Delegation Scaling
	- We noticed processing time increase matches the validator/delegation scaling to around 2500 in OSTN (refer the Delegation Information vs Processing Time graph in the [notebook](https://harmony-one.github.io/harmony-log-analysis/notebooks/OSTN_03_15_processing_time_vs_delegations.html))
	- But processing time doesn't increase a lot when we just scaling delegators to 50k in stn (refer the Delegation Information vs Processing Time graph in the [notebook](https://harmony-one.github.io/harmony-log-analysis/notebooks/stress_test_03_14_processing_time_vs_delegations.html)
 
- Different Economic Activity Processing Time
	- [ostn-03-19](https://harmony-one.github.io/harmony-log-analysis/notebooks/ostn_03_19_processing_time.html)
	- [ostn-03-20](https://harmony-one.github.io/harmony-log-analysis/notebooks/ostn_03_20_processing_time_comparison.html)
	- [new ostn lauch: before vs after](https://harmony-one.github.io/harmony-log-analysis/notebooks/ostn_03_20_processing_time_comparison.html) 
