#!/usr/bin/env python
# coding: utf-8
import glob
import os
from os import path
import json
import pandas as pd
from collections import defaultdict
import gspread
import pickle
import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--network', required = True, help = 'Network to query from')
    args = parser.parse_args()
    
    if args.network:
        network = args.network
    else:
        print('Network is required.')
        exit(1)
        
    base = path.dirname(path.realpath(__file__))
    count_dir = path.abspath(path.join(base, 'count'))
    file_name = path.join(count_dir, 'count_{}.pickle'.format(network))
    
    with open(file_name, 'rb') as f:
        count = pickle.load(f)
        
    df = pd.DataFrame.from_dict(count, orient = 'index')
    df = df.T
    df.rename(columns = {0:'shard-0', 1:'shard-1', 2:'shard-2', 3:'shard-3'}, inplace = True)
    df['total'] = df.sum(axis = 1)

    json_file = path.abspath(path.join(base, 'jsonFileFromGoogle.json'))
    gc = gspread.service_account(json_file)
    sh = gc.open("harmony-tracker-{}".format(network))
    worksheet = sh.get_worksheet(2)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())