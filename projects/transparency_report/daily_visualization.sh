/home/ubuntu/anaconda3/bin/jupyter nbconvert --execute /home/ubuntu/jupyter/harmony-log-analysis/projects/transparency_report/notebook/txs_visualization.ipynb

/home/ubuntu/anaconda3/bin/jupyter nbconvert --execute /home/ubuntu/jupyter/harmony-log-analysis/projects/transparency_report/notebook/daily_visualization.ipynb

cd /home/ubuntu/jupyter/harmony-log-analysis && git add docs/graphs/transparency_report/ 
git commit -m "daily cronjob of transparency report "`date +"%Y_%m_%d"`
git push origin master