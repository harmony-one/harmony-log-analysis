#!/usr/bin/env bash

tmux send-keys -t txs C-c
tmux send-keys -t txs "python3 transaction_data.py --endpoints http://13.52.249.50:9500,http://54.215.235.83:9500,http://3.101.29.219:9500,http://3.101.19.198:9500 --output_file "`date +%"Y_%m_%d"` C-m