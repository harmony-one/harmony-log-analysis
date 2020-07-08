#!/usr/bin/env bash
head -n -2 /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md > /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/temp.md ; mv /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/temp.md /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md
VAR1=`date -d 'yesterday 13:00' '+%Y/%m'`
VAR2=`date '+%Y/%m'`
num=`date -d 'yesterday 13:00' '+%d'`
month=`date -d 'yesterday 13:00' '+%B'`
if [ "$VAR1" != "$VAR2" ]; then
    echo -e "- [`date -d 'yesterday 13:00' '+%Y/%m/%d'`](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/mainnet_`date -d 'yesterday 13:00' '+%Y_%m_%d'`.html)" >> /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md
    head -n 4 /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md > /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/temp.md ; 
    echo -e "\n\n## $month" >> /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/old_report/index.md
    echo -e "$(cat /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md | head -$(( 4+num )) | tail -$num)" >> /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/old_report/index.md ;
    mv /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/temp.md /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md 
    echo -e "\n ###[Old Reports](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/old_report)" >> /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md
else
    echo -e "- [`date -d 'yesterday 13:00' '+%Y/%m/%d'`](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/mainnet_`date -d 'yesterday 13:00' '+%Y_%m_%d'`.html)\n\n### [Old Reports](https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/old_report)" >> /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/index.md
fi

cd /home/ubuntu/jupyter/harmony-log-analysis && git add docs/graphs/test_logs/ && git add docs/notebooks/explorer_mini_logs/ && git add graphs/test_logs/
git commit -m "daily cronjob push graphs "`date +"%Y_%m_%d"`
git push origin master
