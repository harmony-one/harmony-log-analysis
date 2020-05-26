#!/usr/bin/env python
# coding: utf-8

import json
import requests
import logging
from datetime import datetime
from collections import defaultdict
from threading import Thread
import argparse
import os
from os import path
import pickle 
from queue import Queue
import time
import argparse
import copy

base = path.dirname(path.realpath(__file__))
logs = path.abspath(path.join(base, 'logs'))
pkl_dir = path.abspath(path.join(base, 'pickle'))

def new_log(network, date):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("transaction")
    logger.setLevel(logging.INFO)
    filename = path.join(logs, "{}_{}.log".format(network, date))
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

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
        
def getLatestHeader(shard) -> dict:
    url = endpoint[shard]
    method = 'hmy_latestHeader'
    params = []
    return get_information(url, method, params)

def getBlockTransactionCountByNumber(shard, number) -> int:
    url = endpoint[shard]
    method = "hmyv2_getBlockTransactionCountByNumber"
    params = [number]
    return get_information(url, method, params)

def getBlockByNumber(shard, number) -> dict:
    url = endpoint[shard]
    method = 'hmyv2_getBlockByNumber'
    params = [number, {"fullTx":False,"withSigners":False,"InclStaking":False}]
    return get_information(url, method, params)
        

if __name__ == "__main__":
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
        
    directory = [logs, pkl_dir]
    for d in directory:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make directory")
                exit(1)
            
    date = datetime.utcnow().strftime('%Y_%m_%d')
    logger = new_log(network,date)
    
    pkl_file = path.join(pkl_dir,'count_{}.pickle'.format(network))
    if path.exists(pkl_file):
        with open(pkl_file, 'rb') as f:
            total = pickle.load(f)
    else:                     
        total = defaultdict(int)
        
    shard_info = path.join(pkl_dir,'shard_info_{}.pickle'.format(network))
    if path.exists(shard_info):
        with open(shard_info, 'rb') as f:
            prev = pickle.load(f)
    else:
        prev = {0:1, 1:1, 2:1, 3:1}

    while True:
        old_total = total.copy()
        # set up logging
        new_date = datetime.utcnow().strftime('%Y_%m_%d')
        if new_date != date:
            logger = new_log(network, new_date)
        
        # get the latest block number
        curr = defaultdict(int)
        for shard in range(len(endpoint)):
            latest = getLatestHeader(shard)
            if latest != None:
                curr[shard] = latest['result']['blockNumber']  
        
        # get the number of threads
        total_block = 0
        for shard in range(len(endpoint)):
            length = curr[shard] - prev[shard]
            total_block += length
        if total_block == 0:
            time.sleep(5)
            continue  
        
        # set up queue object
        q = Queue()
        
        # output from queue
        def collect_data(q):
            while not q.empty():
                global total
                i, shard = q.get()
                count = getBlockTransactionCountByNumber(shard, i)
                if count != None:
                    total[shard] += count['result']
                if i % 1000 == 1:
                    res = getBlockByNumber(shard, i)
                    if res != None:
                        timestamp = res['result']['timestamp']
                        timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
                        t = {
                            "timestamp": timestamp,
                            "shard": shard,
                             "block": i,
                            "shard-transactions": total[shard],
                            }
                        logger.info(json.dumps(t))
                q.task_done()

        # input to queue
        for shard in range(len(endpoint)):
            for x in range(prev[shard], curr[shard]):
                q.put((x,shard))
        
        # set up thread processing
        num_threads = min(200, total_block)
        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()            
                
        q.join()
        if total != old_total:
            logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} pickle file updated")
            # save txs count to pickle
            with open(pkl_file, 'wb') as f:
                pickle.dump(total, f)
        with open(shard_info, 'wb') as f:
            pickle.dump(curr, f)
        # reset previous block
        prev = copy.deepcopy(curr)           
        time.sleep(5)        