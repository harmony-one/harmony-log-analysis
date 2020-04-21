#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import os
import gzip
import re

def read_data(files, path):
    data = []
    for file in files:
        if "zerolog" in file:
            with gzip.open(path + file) as f:
                for line in f.readlines():
                    if 'error'.encode('utf-8') in line:
                        data.append(json.loads(line))
    return data

def save_data(log_dir, date, group):
    save_dir = "../../logs/node_logs/ostn_" + date + "/"
    files = os.listdir(log_dir)
    data = read_data(files, log_dir)
    df = pd.DataFrame(data, columns = ['level', 'ip', 'error', 'time', 'message'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    df.to_pickle(save_dir +  group + ".pkl")
    
if __name__ == "__main__":

    
    date = input("Please specify the date you want to save data, format '03_29' ")
    pattern = re.compile("([0-9]+).([0-9]+)")
    pattern = re.compile("([0-9]+).*?([0-9]+)")
    date = "_".join(re.findall(pattern, date)[0])
    
    log_dir = input("Please specify the logs directory folder, format: '2020/03/27/001302/validator/tmp_log/log-20200327.001302/' ")
    log_dir = "/home/ubuntu/jupyter/logs/" + log_dir
    
    pattern = re.compile(".*/(.*?)/tmp_log")
    group = re.findall(pattern, log_dir)[0]
    save_data(log_dir, date, group)

