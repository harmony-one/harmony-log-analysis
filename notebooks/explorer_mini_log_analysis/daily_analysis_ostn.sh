
# mkdir -p /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/

/home/ubuntu/anaconda3/bin/jupyter nbconvert --execute /home/ubuntu/jupyter/harmony-log-analysis/notebooks/explorer_mini_log_analysis/daily_report_ostn.ipynb --output /home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/ostn_`date -d 'yesterday 13:00' '+%Y_%m_%d'` --ExecutePreprocessor.timeout=500

