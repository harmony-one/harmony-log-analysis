
/home/ubuntu/anaconda3/bin/jupyter nbconvert --execute /home/ubuntu/jupyter/harmony-log-analysis/projects/explorer_mini_log_analysis/daily_report_mainnet.ipynb --output /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/mainnet_`date -d 'yesterday 13:00' '+%Y_%m_%d'` --no-input --ExecutePreprocessor.timeout=500
