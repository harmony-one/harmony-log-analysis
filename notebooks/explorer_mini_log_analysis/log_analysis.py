#!/usr/bin/env python
# coding: utf-8

import utils
import os
from os import path
import argparse
import pickle
import datetime

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Analyze explorere mini logs')
    parser.add_argument('--start_time', help = 'Select the start time of the time window you want to analyze, e.g: 06:00:00')
    parser.add_argument('--end_time',  help = 'Select the end time of the time window you want to analyze, e.g: 06:00:00')
    parser.add_argument('--start_block', help = 'Select the start block of the block window you want to analyze')
    parser.add_argument('--end_block',  help = 'Select the end block of the block window you want to analyze')
    parser.add_argument('--date', help = 'Select the date you want to analyze, e.g: 2020_04_15')
    parser.add_argument('--ignore_statistic_summary', action = 'store_true', help = 'Not print the statistics sumamry')
    parser.add_argument('--ignore_feature_vs_time_all', action = 'store_true', help = 'Not draw features vs time for all shards')
    parser.add_argument('--feature_vs_block_all', action = 'store_true', help = 'Draw features vs block for all shards in one graph')
    parser.add_argument('--feature_vs_time_per_shard', action = 'store_true', help = 'Draw features vs time per shard')
    parser.add_argument('--feature_vs_block_per_shard', action = 'store_true', help = 'Draw features vs block per shard')
    parser.add_argument('--staking_feature_vs_time_per_shard', action = 'store_true', help = 'Draw staking features vs time per shard')
    parser.add_argument('--staking_feature_vs_block_per_shard', action = 'store_true', help = 'Draw staking features vs block per shard')

    args = parser.parse_args()

    if not args.date:
        yesterday = datetime.date.today()-datetime.timedelta(days=1)
        date = yesterday.strftime("%Y_%m_%d")
    else:
        date = args.date.replace("-","_")
        
    name = "ostn_"+ date +".log"
    log_dir = "/home/ubuntu/jupyter/monitor/mini_explorer/data/" + name
    data = utils.read_data(log_dir)
    
    if (args.start_time and not args.end_time) or (not args.start_time and args.end_time):
        print("Need to specify both start time and end time")
        exit(1)
    
    if (args.start_block and not args.end_block) or (not args.start_block and args.end_block):
        print("Need to specify both start block and end block")
        exit(1)
        
    if args.start_time and args.end_time:
        start_time = date.replace("_","-") + " " + args.start_time
        end_time = date.replace("_","-") + " " + args.end_time
        shard = utils.data_processing(data, start_time, end_time)
        
    elif args.start_block and args.end_block:
        start_block = int(args.start_block)
        end_block = int(args.end_block)
        shard = utils.data_processing(data, start_block, end_block)
    else:
        shard = utils.data_processing(data)
                        
    param = dict()
    if args.ignore_statistic_summary:
        param['ignore_printing_statistics_summary'] = True
    else:
        param['ignore_printing_statistics_summary'] = False
    
    if args.ignore_feature_vs_time_all:
        param['ignore_drawing_features_vs_time'] = True
    else:
        param['ignore_drawing_features_vs_time'] = False
                        
    if args.feature_vs_block_all:
        param['ignore_drawing_features_vs_block'] = False
    else:
        param['ignore_drawing_features_vs_block'] = True
    
    if args.feature_vs_time_per_shard:
        param['ignore_drawing_features_vs_time_per_shard'] = False
    else:
        param['ignore_drawing_features_vs_time_per_shard'] = True   
    
    if args.feature_vs_block_per_shard:
        param['ignore_drawing_features_vs_block_per_shard'] = False
    else:
        param['ignore_drawing_features_vs_block_per_shard'] = True                        
    
    if args.staking_feature_vs_time_per_shard:
        param['ignore_drawing_staking_features_vs_time_per_shard'] = False
    else:
        param['ignore_drawing_staking_features_vs_time_per_shard'] = True    
    
    if args.staking_feature_vs_block_per_shard:
        param['ignore_drawing_staking_features_vs_block_per_shard'] = False
    else:
        param['ignore_drawing_staking_features_vs_block_per_shard'] = True      
                        
    with open('./tmp/shard.pkl', 'wb') as f:
        pickle.dump(shard, f)
 
    with open('./tmp/param.pkl', 'wb') as f:
        pickle.dump(param, f)
                        
    output_dir = "/home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/explorer_mini_logs/part/" + date
    os.system('jupyter nbconvert --execute log_analysis.ipynb --output {:s} --ExecutePreprocessor.timeout=500'.format(output_dir))
    os.system('git add ../../docs/notebooks/explorer_mini_logs/part/')
    os.system('git add ../../docs/graphs/test_logs/ostn/' + date + '/part')
    os.system('git add ../../graphs/test_logs/ostn/' + date + '/part')
    message = 'automate push graphs {:s}'.format(date)
    os.system('git commit -m "{:s}"'.format(message))
    os.system("git push -u origin master")
    print("check the link: https://harmony-one.github.io/harmony-log-analysis/notebooks/explorer_mini_logs/part/" + date)

