#!/usr/bin/env python
# coding: utf-8

import os
from os import path
import gzip
import re
import json
import pandas as pd

env = os.environ.copy()
timeout = 350
base = path.dirname(path.realpath(__file__))

def download_data(date, node):
    try:
        path = "s3://harmony-benchmark/logs/mainnet/{:s}".format(node)
        log = "zerolog-validator-{:s}-9000-{:s}*.gz".format(node, date)
        os.system('python3 ./ops.py log download-from-path {:s} --exclude "*" --include "{:s}"'.format(path, log))

    except:
        print("meet error in downloading data from s3")
        exit(1)

def read_data(files, log_dir, date):
    data = []
    for file in files:
        if date in file:
            with gzip.open(path.join(log_dir,file)) as f:
                for line in f.readlines():
                    if 'error'.encode('utf-8') in line:
                        data.append(json.loads(line))
    return data

def save_data(log_dir, date):
    save_dir = "/home/ubuntu/jupyter/harmony-log-analysis/logs/node_logs/"
    files = os.listdir(log_dir)
    data = read_data(files, log_dir, date)
    if not data:
        print("The node with the date was not found in logs")
        exit(1)
    try:
        df = pd.DataFrame(data, columns = ['level', 'ip', 'error', 'time', 'message'])
    except:
        print("meet error in creating dataframe")
        exit(1)
    if not path.exists(save_dir):
        os.makedirs(save_dir)
    df.to_pickle(path.join(save_dir, "mainnet_{:s}.pkl".format(date)))
    return save_dir

    
if __name__ == "__main__":
    date = input("Please specify the date you want to save data, format '2020-03-29' ")
    if "_" in date or "/" in date:
        print("the date format is not correct")
        exit(1)
        
    node = input("Please specify the node you want to analyze, format '3.112.219.248' ")

    log_dir = "/home/ubuntu/jupyter/logs/mainnet/{:s}".format(node)
    
    os.chdir("/home/ubuntu/ops/")
    download_data(date, node)
    print("Successfully download data and save it to {:s}".format(log_dir))
    
    os.chdir(base)
    save_dir = save_data(log_dir, date)
    print("Successfully save data to {:s}".format(save_dir))
    
    output_dir = "/home/ubuntu/jupyter/harmony-log-analysis/docs/notebooks/error_analysis/mainnet/{:s}/".format(node)
    if not path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = path.join(output_dir, date)
    os.system('jupyter nbconvert --execute notebooks/single_node_error.ipynb --output {:s} --ExecutePreprocessor.timeout=500'.format(output_dir))
    os.system('git add ../../docs/notebooks/error_analysis/{:s}/'.format(node))
    os.system('git add ../../docs/graphs/error_analysis/')
    message = 'automate push mainnet node error analysis graphs {:s}'.format(date)
    os.system('git commit -m "{:s}"'.format(message))
    os.system("git push -u origin master")
    print("check the link later: https://harmony-one.github.io/harmony-log-analysis/notebooks/error_analysis/{:s}/{:s}".format(node, date))
