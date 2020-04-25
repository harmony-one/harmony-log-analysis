#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import os
import gzip
import re
import subprocess

env = os.environ.copy()
timeout = 120
base = os.path.dirname(os.path.realpath(__file__))

def download_data(date, log_dir):
    try:
        path = "s3://harmony-benchmark/logs/os/{:s}".format(log_dir)
        log = "zerolog-validator-*{:s}*.gz".format(date)
        os.system('python3 ./ops.py log download-from-path {:s} --exclude "*" --include "{:s}"'.format(path, log))
        
    except:
        print("meet error in downloading data from s3")
        exit(1)

def read_data(files, path, date):
    data = []
    for file in files:
        if date in file:
            with gzip.open(path + file) as f:
                for line in f.readlines():
                    if 'error'.encode('utf-8') in line:
                        data.append(json.loads(line))
    return data

def save_data(log_dir, date, group):
    save_dir = "/home/ubuntu/jupyter/harmony-log-analysis/logs/node_logs/ostn_{:s}/".format(date)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:
        pkl_dir = save_dir +  group + ".pkl"
        print("Successfully process data and save dataframe to {:s}".format(pkl_dir)) 
        return pkl_dir
    files = os.listdir(log_dir)
    data = read_data(files, log_dir, date)
    df = pd.DataFrame(data, columns = ['level', 'ip', 'error', 'time', 'message'])
    pkl_dir = save_dir +  group + ".pkl"
    df.to_pickle(pkl_dir)
    return pkl_dir
    
def _list_aws_dir(directory):
    cmd = ['aws', 's3', 'ls', directory]
    return [n.replace('PRE', '').strip() for n in
            subprocess.check_output(cmd, env=env, timeout=timeout).decode().split("\n") if n]
    
    
if __name__ == "__main__":

    date = input("Please specify the date you want to download, format '20/04/14' ")
    directory = "s3://harmony-benchmark/logs/os/{:s}/".format(date)
    print("Available option time folders:")
    for i in _list_aws_dir(directory):
        print(i.replace("/",""))
    time = input("please specify the time folder you want to download, format '19:35:10' ")

    directory = os.path.join(directory, time)
    leader = os.path.join(directory, 'leader/tmp_log/')
    validator = os.path.join(directory, 'validator/tmp_log/')
    leader = os.path.join(leader, _list_aws_dir(leader)[0])
    validator = os.path.join(leader, _list_aws_dir(validator)[0])
    
    pattern = re.compile("([0-9]+).*?([0-9]+).*?([0-9]+)")
    date = "_".join(re.findall(pattern, date)[0])
    
    os.chdir("/home/ubuntu/ops/")
    download_data(date, leader)
    leader_dir = "/home/ubuntu/jupyter/" + leader.replace("s3://harmony-benchmark/","")
    print("Successfully download leader data and save it to {:s}".format(leader_dir))
    pkl_dir = save_data(leader_dir, date, "leader")
    print("Successfully process data and save dataframe to {:s}".format(pkl_dir)) 
    
    download_data(date, validator)
    validator_dir = "/home/ubuntu/jupyter/" + validator.replace("s3://harmony-benchmark/","")
    print("Successfully download validator data and save it to {:s}".format(validator_dir))
    pkl_dir = save_data(leader_dir, date, "validator")
    print("Successfully process data and save dataframe to {:s}".format(pkl_dir)) 
    
    os.chdir(base)
    output_dir = "/home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/error_analysis/ostn/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = os.path.join(output_dir, date)
    os.system('jupyter nbconvert --execute notebooks/ostn_network_error.ipynb --output {:s} --ExecutePreprocessor.timeout=500'.format(output_dir))
    os.system('git add ../../docs/notebooks/error_analysis/ostn/')
    os.system('git add ../../docs/graphs/error_analysis/')
    message = 'automate push ostn network error analysis graphs {:s}'.format(date)
    os.system('git commit -m "{:s}"'.format(message))
    os.system("git push -u origin master")
    print("check the link later: https://harmony-one.github.io/harmony-log-analysis/notebooks/error_analysis/ostn/{:s}".format(date))
    

