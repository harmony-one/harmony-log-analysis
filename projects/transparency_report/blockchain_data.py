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

base = path.dirname(path.realpath(__file__))
logs = path.abspath(path.join(base, 'logs'))
data = path.abspath(path.join(base, 'data'))

def new_log(shard):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("blockchain")
    logger.setLevel(logging.INFO)
    filename = path.join(logs, "blockchain_{}.log".format(shard))
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas.')
    args = parser.parse_args()
    endpoint = []
    if args.endpoints:
        endpoint = [x.strip() for x in args.endpoints.strip().split(',')]        
    else:
        print('List of endpoints is required.')
        exit(1)
        
    directory = [logs, data]
    for d in directory:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make directory")
                exit(1)

    shard_info = path.join(data,'blockchain_shard_info.txt')
#     if path.exists(shard_info):
#         with open(shard_info, 'r') as f:
#             prev = json.load(f, object_hook=lambda d: {int(k): v for k, v in d.items()})
#     else:
#         prev = {0:0, 1:0, 2:0, 3:0}
    curr = defaultdict(int)
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
            
        with open(shard_info, 'w') as f:
            json.dump(curr, f)

    prev = {0:3955244, 1:2364555, 2:0, 3:0}
    for shard in range(len(endpoint)):
        total_block = 0
        length = curr[shard] - prev[shard]
        total_block += length
        logger = new_log(shard)
        # set up queue object
        q = Queue()
        if shard == 1:
            res = blockchain.get_block_by_number(2364553, endpoint=endpoint[shard], include_full_tx=False)
            if res != None:
                gasLimit = int(res['gasLimit'],16)
                gasUsed = int(res['gasUsed'], 16)
                size = int(res['size'],16)
                timestamp = int(res['timestamp'],16)
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
                t = {
                    "timestamp": timestamp,
                    "shard": shard,
                    "block": i,
                    "gasLimit": gasLimit,
                    "gasUsed": gasUsed,
                    "size": size,
                    }
                logger.info(json.dumps(t))
        # output from queue
        def collect_data(q):
            while not q.empty():
                i = q.get()

                res = blockchain.get_block_by_number(i, endpoint=endpoint[shard], include_full_tx=False)
                if res != None:
                    gasLimit = int(res['gasLimit'],16)
                    gasUsed = int(res['gasUsed'], 16)
                    size = int(res['size'],16)
                    timestamp = int(res['timestamp'],16)
                    timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
                    t = {
                        "timestamp": timestamp,
                        "shard": shard,
                        "block": i,
                        "gasLimit": gasLimit,
                        "gasUsed": gasUsed,
                        "size": size,
                        }
                    logger.info(json.dumps(t))

                q.task_done()

        # input to queue
#         for shard in range(len(endpoint)):
        for x in range(prev[shard], curr[shard]):
            q.put((x))

        # set up thread processing
        num_threads = min(200, total_block)
        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()            

        q.join()

