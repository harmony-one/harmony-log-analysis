#!/usr/bin/env bash

cd /home/ubuntu/jupyter/harmony-log-analysis && git add docs/graphs/test_logs/ && git add docs/notebooks/explorer_mini_logs/ && git add graphs/test_logs/
git commit -m "daily cronjob push graphs "`date +"%Y_%m_%d"`
git push origin master
head -n -2 /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md > /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/temp.md ; mv /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/temp.md /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md
echo -e "- [`date -d 'yesterday 13:00' '+%Y/%m/%d'`](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/mainnet_`date -d 'yesterday 13:00' '+%Y_%m_%d'`.html)\n\n### [Old Reports](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/old_report/index.md)" >> /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md
