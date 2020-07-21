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
from queue import Queue
import time
import argparse
import pyhmy
from pyhmy import (
    blockchain
)
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

base = path.dirname(path.realpath(__file__))
logs = path.abspath(path.join(base, 'logs'))
txt_dir = path.abspath(path.join(base, 'txt'))
json_dir = "/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/credential"

def new_log():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("stakingTxs")
    logger.setLevel(logging.INFO)
    filename = path.join(logs, "stakingTxsCount.log")
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required = True, help = 'Endpoints to query from')
    args = parser.parse_args()

    if args.endpoint:
        endpoint = args.endpoint    
    else:
        print('Endpoint is required.')
        exit(1)
        
    directory = [logs, txt_dir]
    for d in directory:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make directory")
                exit(1)
            
    logger = new_log()
    
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})  
    ref = db.reference('total-stakingTxs-count')
    
    count_file = path.join(txt_dir,'stakingTxs.txt')
    if path.exists(count_file):
        with open(count_file, 'r') as f:
            total = int(f.read())
    else:                     
        total = 0
        
    shard_info = path.join(txt_dir,'block_info.txt')
    if path.exists(shard_info):
        with open(shard_info, 'r') as f:
            prev = int(f.read())
    else:
        pre_staking = blockchain.get_prestaking_epoch(endpoint)
        prev = 16384*(pre_staking-1)+344064
         
    while True:
        # get the latest block number
        old_total = total
        latest = blockchain.get_latest_header(endpoint)
        if latest != None:
            curr = latest['blockNumber']  
        # get the number of threads
        total_block = curr - prev
        if total_block == 0:
            time.sleep(5)
            continue  
        # set up queue object
        q = Queue()

        # output from queue
        def collect_data(q):
            while not q.empty():
                global total
                i = q.get()
                res = blockchain.get_block_by_number(i, endpoint, include_full_tx=False)
                if res != None:
                    total += len(res['stakingTransactions'])
                    if i % 1000 == 1:
                        timestamp = int(res['timestamp'],16)
                        timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
                        t = {
                            "timestamp": timestamp,
                            "block": i, 
                            "count": total,
                            }
                        logger.info(json.dumps(t))
                        with open(count_file, 'w') as f:
                            f.write(str(total))
                        with open(shard_info, 'w') as f:
                            f.write(str(i))
                      
                q.task_done()

        # input to queue
        for x in range(prev, curr):
            q.put((x))
        
        # set up thread processing
        num_threads = min(200, total_block)
        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()            
                
        q.join()
        
        with open(count_file, 'w') as f:
            f.write(str(total))
        with open(shard_info, 'w') as f:
            f.write(str(curr))
        prev = curr
        print("update count and shard info in txt file")
        
        if old_total != total:
            ref.set(total)

        time.sleep(10)
        