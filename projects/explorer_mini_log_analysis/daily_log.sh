#!/usr/bin/env bash

#tmux a -t mini_explorer
tmux send-keys -t mini_explorer C-c
tmux send-keys -t mini_explorer "python3 mini_explorer.py --endpoints https://api.s0.os.hmny.io,https://api.s1.os.hmny.io,https://api.s2.os.hmny.io,https://api.s3.os.hmny.io --output_file ostn_"`date +%"Y_%m_%d"` C-m
tmux send-keys -t mainnet-explorer-mini C-c
tmux send-keys -t mainnet-explorer-mini "python3 mini_explorer.py --endpoints https://api.s0.t.hmny.io,https://api.s1.t.hmny.io,https://api.s2.t.hmny.io,https://api.s3.t.hmny.io --no_staking --output_file mainnet_"`date +%"Y_%m_%d"` C-m
