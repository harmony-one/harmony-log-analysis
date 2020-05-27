#!/usr/bin/env python
# coding: utf-8

import requests
import json
from collections import defaultdict
from threading import Thread
from queue import Queue
import logging
from datetime import datetime
import os
from os import path
import time
import argparse
import pickle 
import firebase_admin
from firebase_admin import credentials
# from firebase_admin import db
from firebase_admin import firestore
import copy
import numpy as np
import pyhmy
from pyhmy import rpc

base = path.dirname(path.realpath(__file__))
json_dir = path.abspath(path.join(base, 'credential'))
log_dir = path.abspath(path.join(base, 'logs'))
pkl_dir = path.abspath(path.join(base, 'pickle'))

def new_log(date, network):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("uptime")
    logger.setLevel(logging.INFO)
    filename = "uptime_{}_{}.log".format(network, date)
    file_handler = logging.FileHandler(path.join(log_dir, filename))
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

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
    
    directory = [log_dir, pkl_dir, json_dir]
    for i in directory:
        if not path.exists(i):
            try:
                os.mkdir(i)
            except:
                print("Could not make data directory")
                exit(1)
    date = datetime.utcnow().strftime('%Y_%m_%d')
    logger = new_log(date, network)
    
    # the block when we enter into open-staking period
    curr_dict = {0: 3375104, 1: 3286736, 2: 3326152, 3: 3313571}

#     total = 0
#     for shard in range(len(endpoint)):
#         length = curr[shard] - prev[shard]
#         total += length
  
    shard_info = path.join(pkl_dir,'shard_info_{}.pickle'.format(network))
    if path.exists(shard_info):
        with open(shard_info, 'rb') as f:
            number = pickle.load(f)
    else:
        number = 0
    block_num = np.arange(number+1, 3309002, 30000).tolist()
    for n in range(len(block_num)-1):
        prev = block_num[n]
        curr = block_num[n+1]
        
        count_file = path.join(pkl_dir,'signer_count_{}.pickle'.format(network))
        if path.exists(count_file):
            with open(count_file, 'rb') as f:
                count = pickle.load(f)
        else:                     
            count = defaultdict(dict)
        
        total_block = 30000
        # set up queue object
        q = Queue()

        # output from queue
        def collect_data(q):
            while not q.empty():
                global count
                i, shard = q.get()
                fail = True
                while fail:
                    try:
                        signer = rpc.blockchain.get_block_signers(i, endpoint[shard], 60)
                        fail = False
                    except rpc.exceptions.RequestsTimeoutError:
                        time.sleep(10)
                        pass
                if signer:
                    for s in set(signer):
                        if s not in count[shard]:
                            count[shard][s] = 1
                        else:
                            count[shard][s] += 1
                    if (i % 1000 == 1) and (shard == 0):                                   
                        with open(count_file, 'wb') as f:
                            pickle.dump(count, f)
                        logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} signer_count pickle file updated, current block number {i}")
                        
                        with open(shard_info, 'wb') as f:
                            pickle.dump(i, f)
                        logger.info(f"tracking block number {i}")
                else:
                    t = {
                        'block-num': i,
                        'reason': f"Block {i} had a null response: {signer}"
                        }
                    logger.info(json.dumps(t))
                    
                time.sleep(5)
                q.task_done()
                
                
        # input to queue
#         min_start = min(prev.values())
#         max_end = max(curr.values())
        for x in range(prev,curr):
            for shard in range(len(endpoint)):
#                 if prev[shard] <= x <= curr[shard]:
                q.put((x,shard))
                    
        # set up thread processing
        num_threads = min(100, total_block)
        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()            
         
        q.join()

        with open(count_file, 'wb') as f:
            pickle.dump(count, f)
        logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} signer_count pickle file updated, from {prev} to {curr-1}")
        
        time.sleep(15) 
        


