# Mini Explorer Log Analysis
This project provides the analysis for the [mini explorer logs](https://github.com/harmony-one/monitor/tree/master/mini_explorer). It has two versions. 

One is to produce automatic daily report in github pages, inclduing statistics summary and visualization on features vs time. It will update new report on 0:10 UTC everyday, check by changing the date in the [link](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/2020_04_16).

The second is to provide customization for the report, like selecting time window, block window, and choose to draw graphs per shard or all shards, draw staking features or all features. Check the instruction of the running [commands](https://github.com/harmony-one/harmony-log-analysis/tree/master/projects/explorer_mini_log_analysis#commands) below. After running the command, it will print the github page [link](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/part/2020_04_16) for you to visit. 

## Content
### Statistics Summary 
- transaction per second, time per block, size, gas.
### Visualization
- Features vs Time / Block Height (with all shards/per shard): staking transaction per second, total transaction per second, transaction per second, time per block, size, gas;
- Staking Features vs Time / Block Height (per shard): total staking transactions per second, create validator per second, edit validator per second, delegate per second, undelegate per second, collect rewards per second.

## Environment
The whole pipeline of collecting and analyzing the logs is built on [Virtual Machine](http://analytics.hmny.io/terminals/3). For password, please contact @Yishuang | harmony#6899 on discord or @ivorytowerdds on github.

## Commands
Run command: `python3 log_analysis.py`, default is to print the statistic summary and draw features vs time for all shards in one graph for yesterday's (UTC) one-day log.

If you don't want to print the statistic summary, add the option `ignore_statistic_summary`;

If you don't want to draw features vs time for all shards in one graph, add the option `ignore_feature_vs_time_all`;

To select specific time window to analyze, add the options `--start_time 06:00:00` and `--end_time 08:00:00`;

To select specific block window to analyze, add the options `--start_block 10000` and `--end_time 12000`;

To select specific date of log to analyze, add the option `--date 2020_04_16`;

To draw features vs block for all shards in one graph, add the option `--feature_vs_block_all`;

To draw features vs time per shard, add the option `--feature_vs_time_per_shard`;

To draw features vs block per shard, add the option `--feature_vs_block_per_shard`;

To draw staking features vs time, add the option `--staking_feature_vs_time_per_shard`;

To draw staking features vs block, add the option `--staking_feature_vs_block_per_shard`.


