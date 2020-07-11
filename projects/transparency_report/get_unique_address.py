#!/usr/bin/env python
# coding: utf-8
import json
import requests
import logging
from datetime import datetime
from collections import defaultdict
from threading import Thread
import time
from queue import Queue
from os import path
import os
import argparse
import pickle 
import time
import pandas as pd
import copy
import re
import pyhmy 
from pyhmy import (
    blockchain,
    rpc
)


base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'data'))
log_dir = path.abspath(path.join(base, 'logs'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas')
    args = parser.parse_args()
    endpoint = []
    if args.endpoints:
        endpoint = [x.strip() for x in args.endpoints.strip().split(',')]        
    else:
        print('List of endpoints is required.')
        exit(1)

    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("address")
    logger.setLevel(logging.INFO)
    filename = path.join(log_dir, "address_growth.log")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    directory = [data, log_dir]
    for d in directory:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make address directory")
                exit(1)

    addr_file = path.join(data,'unique_address.txt')
    if path.exists(addr_file):
        # restart from last records
        address = set()
        with open(addr_file, 'r') as f:
            for line in f:
                curr = line[:-1]
                address.add(curr)       
    else: 
        # first time setup: since some foundational nodes doesn't have txs history
        filename = path.join(data, 'all_foundational.txt')
        address = set()
        with open(filename, 'r') as f:
            for line in f:
                res = line[:-1]
                address.add(res) 
        with open(addr_file, 'w') as f:
            for i in address:
                f.write('%s\n' % i)

    addr_length = len(address)
    res = blockchain.get_block_by_number(0, endpoint[0], include_full_tx=True)
    timestamp = datetime.fromtimestamp(int(res['timestamp'],16)).strftime('%Y-%m-%d')
    t = {
        "timestamp": timestamp,
        "count": addr_length,
        "block": 0,
        "shard": 0
    }
    logger.info(json.dumps(t))
    
    res = blockchain.get_block_by_number(502988, endpoint[0], include_full_tx=True)
    timestamp = datetime.fromtimestamp(int(res['timestamp'],16)).strftime('%Y-%m-%d')
    t = {
        "timestamp": timestamp,
        "count": 1,
        "block": 502988,
        "shard": 0
    }
    logger.info(json.dumps(t))
    
    shard_info = path.join(data,'shard_info.txt')
    if path.exists(shard_info):
        with open(shard_info, 'r') as f:
            prev = json.load(f, object_hook=lambda d: {int(k): v for k, v in d.items()})
    else:
        prev = {0:559753, 1:667478, 2:565021, 3:559753}
    curr = defaultdict(int)
    
    while True:
        for shard in range(len(endpoint)):
            fail = True
            while fail:
                try:
                    latest = blockchain.get_latest_header(endpoint[shard])
                    fail = False
                except rpc.exceptions.RequestsTimeoutError:
                    time.sleep(10)
                    pass
            if latest:
                curr[shard] = latest['blockNumber'] 
        total = 0
        for shard in range(len(endpoint)):
            length = curr[shard] - prev[shard]
            total += length
        if total == 0:
            # means no new change for any shard
            time.sleep(30)
            continue

        q = Queue()
        def collect_data(q): 
            while not q.empty():
                global address
                i, shard = q.get()
                try:
                    res = blockchain.get_block_by_number(i, endpoint[shard], include_full_tx=True)
                except rpc.exceptions.RequestsTimeoutError:
                    pass
                if res:
                    transactions = res['transactions']
                    if transactions:
                        for txs in transactions:
                            if (txs['from'] not in address) or (txs['to'] not in address):
                                timestamp = res['timestamp']
                                date = datetime.fromtimestamp(int(timestamp,16)).strftime('%Y-%m-%d')
                                if (txs['from'] not in address) and (re.match('one1', txs['from']) != None):
                                    address.add(txs['from'])
                                    with open(addr_file, 'a') as f:
                                        f.write('%s\n' % txs['from'])
                                if (txs['to'] not in address) and (re.match('one1', txs['to']) != None):
                                    address.add(txs['to'])  
                                    with open(addr_file, 'a') as f:
                                        f.write('%s\n' % txs['to'])

                                t = {
                                "timestamp": date,
                                "count": 1,
                                "block": i,
                                "shard": shard
                                }
                                logger.info(json.dumps(t))
                q.task_done()

        start = min(prev.values())
        end = min(curr.values())
        for x in range(start, end):
            for shard in range(len(endpoint)):
                if x >= prev[shard] and x <= curr[shard]:
                    q.put((x, shard))

        num_threads = min(100, total)
        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()

        q.join()
        
        with open(shard_info, 'w') as f:
            json.dump(curr, f)
        prev = copy.deepcopy(curr)  
        time.sleep(30)



