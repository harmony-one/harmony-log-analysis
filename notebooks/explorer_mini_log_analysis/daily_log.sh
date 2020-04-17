#!/usr/bin/env bash

#tmux a -t mini_explorer
tmux send-keys -t mini_explorer C-c
tmux send-keys -t mini_explorer "python3 mini_explorer.py --endpoints https://api.s0.os.hmny.io,https://api.s1.os.hmny.io,https://api.s2.os.hmny.io,https://api.s3.os.hmny.io --output_file ostn_"`date +%"Y_%m_%d"` C-m
#tmux send-keys -t mini_explorer C-b-d
