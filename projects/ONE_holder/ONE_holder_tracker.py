#!/usr/bin/env python
# coding: utf-8

import json
import requests
import pandas as pd
import numpy as np
import os
from os import path
from datetime import datetime
from threading import Thread
import logging
from collections import defaultdict
# import gspread
import pickle
import argparse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import pyhmy
from pyhmy import rpc

def new_log(network):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ONE_holder")
    logger.setLevel(logging.INFO)
    track_file = path.join(log_dir, "tracking_{}.log".format(network))
    if path.exists(track_file):
        os.remove(track_file)
    file_handler = logging.FileHandler(track_file)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def read_data(path):
    data = []
    with open(path, errors='ignore') as f:
        for line in f.readlines():
            try: 
                data.append(line.strip())
            except:
                print(f'can\'t read {line}')
    return data

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json; charset=utf8'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
    except requests.exceptions.ConnectionError as e:
        print("Error: connection error")
        time.sleep(5)
        return None
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        r.json()
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    return r.json()
    
def getBalance(shard, address) -> int:
    url = endpoint[shard]
    method = 'hmyv2_getBalance'
    params = [address, 'latest']
    return get_information(url, method, params)

def getTransactionsCount(shard, address) -> int:
    url = endpoint[shard]
    method = 'hmy_getTransactionsCount'
    params = [address, 'ALL']
    return get_information(url, method, params)


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas.')
    parser.add_argument('--network', required = True, help = 'Network to query from')
    args = parser.parse_args()
    endpoint = []
    if args.endpoints:
        endpoint = [x.strip() for x in args.endpoints.strip().split(',')]        
    else:
        print('List of endpoints is required.')
        exit(1)
    if args.network:
        network = args.network
    else:
        print('Network is required.')
        exit(1)

    base = path.dirname(path.realpath(__file__))
    addr_dir = path.abspath(path.join(base, 'address'))
    log_dir = path.abspath(path.join(base, 'logs'))
    csv_dir = path.abspath(path.join(base, 'csv/{}'.format(network)))
    json_dir = path.abspath(path.join(base, 'credential'))
#     html_dir = path.abspath(path.join(base, 'html'))
    
    folder = [log_dir, csv_dir, addr_dir]
    for f in folder:
        if not path.exists(f):
            try:
                os.makedirs(f)
            except:
                print("Could not make data directory")
                exit(1)
    
    logger = new_log(network)
    
    filename = path.join(addr_dir, 'address_{}.pickle'.format(network))
    with open(filename, 'rb') as f:
        address = pickle.load(f)
    address = list(address)
    thread_lst = defaultdict(list)
    for i in range(len(address)):
        thread_lst[i%200].append(i)

    def collect_data(x):
        for i in thread_lst[x]: 
            balance = 0
            transaction = 0
            addr = address[i]
            balance = 0
            for shard in range(len(endpoint)):
                res = rpc.account.get_balance(addr, endpoint[shard])
                if res != None:
                    balance += res/1e18
                    count = getTransactionsCount(shard, addr)
                    if count != None:
                        if 'result' in count:
                            transaction += count['result']
            t = {
                "address": addr,
                "balance": np.round(balance,2),
                "transaction-count": transaction
            }
            logger.info(json.dumps(t))

    threads = []
    for x in range(200):
        threads.append(Thread(target = collect_data, args = [x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    file_name = path.join(log_dir, "tracking_{}.log".format(network))
    result = []
    with open(file_name, errors='ignore') as f:
        for line in f.readlines():
            try: 
                result.append(json.loads(line))
            except:
                print('bad json: ', line)
    df = pd.DataFrame(result)
    df.sort_values(by=['balance'], ascending=False, inplace = True) 
    df['balance'] = df['balance'].apply(lambda c: '{:,.2f}'.format(c))
    df.reset_index(drop = True, inplace = True)
    data = json.loads(df.to_json())
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})
    ref = db.reference('one-holder')
    ref.set(data)
    print(f"total running time: {time.time()-start}")
#     csv_name = "{}_{}_tracker.csv".format(network, datetime.now().strftime("%Y_%m_%d %H:%M:%S"))
#     df.to_csv(path.join(csv_dir, csv_name))
    
#     html_name = "{}_{}_tracker.html".format(network, datetime.now().strftime("%Y_%m_%d %H:%M:%S"))
#     df.to_html(path.join(html_dir, html_name))
                                
#     json_file = path.join(base, 'credential/jsonFileFromGoogle.json')
#     gc = gspread.service_account(json_file)
#     sh = gc.open("harmony-{}-tracker".format(network))
#     worksheet = sh.get_worksheet(0)
#     worksheet.update([df.columns.values.tolist()] + df.values.tolist())