#!/usr/bin/env python
# coding: utf-8
import logging
from datetime import datetime
import time
from collections import defaultdict
from threading import Thread
from queue import Queue
from os import path
import os
import argparse
import pickle 
import pandas as pd
import copy
import pyhmy 
from pyhmy import rpc

base = path.dirname(path.realpath(__file__))
pkl_dir = path.abspath(path.join(base, 'pickle'))
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
    
    data = [pkl_dir, log_dir]
    for i in data:
        if not path.exists(i):
            try:
                os.mkdir(i)
            except:
                print("Could not make address directory")
                exit(1)
                
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("viewID")
    logger.setLevel(logging.INFO)
    filename = "./logs/get_viewID.log"
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    pkl_file = path.join(pkl_dir,'viewID.pkl')
    if path.exists(pkl_file):
        # restart from last records
        with open(pkl_file, 'rb') as f:
            id_dict = pickle.load(f)
    else: 
        id_dict = defaultdict(dict)
        
    shard_info = path.join(pkl_dir,'shard_info.pkl')
    if path.exists(shard_info):
        with open(shard_info, 'rb') as f:
            prev = pickle.load(f)
    else:
        prev = {0:1, 1:1, 2:1, 3:1}

    while True:
        curr = defaultdict(int)
        for shard in range(len(endpoint)):
            fail = True
            while fail:
                try:
                    latest = rpc.blockchain.get_latest_header(endpoint[shard])
                    fail = False
                except rpc.exceptions.RequestsTimeoutError:
                    time.sleep(10)
                    pass
            if latest:
                curr[shard] = latest['blockNumber'] 
            else:
                curr[shard] = prev[shard]
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
                global id_dict
                i, shard = q.get()
                if i in id_dict[shard]:
                    continue
                fail = True
                while fail:
                    try:
                        res = rpc.blockchain.get_block_by_number(i, endpoint[shard], include_full_tx=False)
                        fail = False
                    except rpc.exceptions.RequestsTimeoutError:
                        time.sleep(20)
                        pass
                if res:
                    id_dict[shard][i] = int(res['viewID'],16)
                    if i % 1000 == 1:      
                        with open(pkl_file, 'wb') as f:
                            pickle.dump(id_dict, f)
                        logger.info(f"Finished processing block {i}, shard {shard}, pickle file updated")                        
                q.task_done()
        
        min_start = min(prev.values())
        max_end = max(curr.values())
        for x in range(min_start, max_end):
            for shard in range(len(endpoint)):
                if prev[shard] <= x <= curr[shard]:
                    q.put((x,shard))
                
        num_threads = min(100, total)

        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()

        q.join()
      
        with open(pkl_file, 'wb') as f:
            pickle.dump(id_dict, f)

        # deep copy dictionary
        prev = copy.deepcopy(curr)  
        # to quickly consume when any request error happen
        with open(shard_info, 'wb') as f:
            pickle.dump(prev, f)
        logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} pickle file updated")
        time.sleep(30)