#!/usr/bin/env bash

cd /home/ubuntu/jupyter/harmony-log-analysis && git add docs/graphs/test_logs/ostn/ && git add docs/notebooks/explorer_mini_logs/ && git add graphs/test_logs/ostn/
git commit -m "daily cronjob push graphs"`date +"%Y_%m_%d"`
git push origin master
echo "you can check the link: https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/"`date -d "yesterday 13:00" "+%Y_%m_%d"`
