#!/usr/bin/env bash

cd /home/ubuntu/jupyter/harmony-log-analysis && git add docs/graphs/test_logs/ && git add docs/notebooks/explorer_mini_logs/ && git add graphs/test_logs/
git commit -m "daily cronjob push graphs "`date +"%Y_%m_%d"`
git push origin master
