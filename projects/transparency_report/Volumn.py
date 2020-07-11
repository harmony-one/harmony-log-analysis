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

def new_log():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("volumn")
    logger.setLevel(logging.INFO)
    filename = path.join(logs, "volumn.log")
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
        
    directory = [logs]
    for d in directory:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make directory")
                exit(1)
            
    logger = new_log()
    
    prev = {0:1, 1:1, 2:1, 3:1}
    curr = {0: 3797299, 1:3769233, 2:3806793, 3:3806793}
    while True:
        # get the number of threads
        total_block = 0
        for shard in range(len(endpoint)):
            length = curr[shard] - prev[shard]
            total_block += length
        
        # set up queue object
        q = Queue()
        
        # output from queue
        def collect_data(q):
            while not q.empty():
                global total
                i, shard = q.get()
                res = blockchain.get_block_by_number(i, endpoint=endpoint[shard], include_full_tx=True)
                if res != None:
                    transactions = res['transactions']
                    for txs in transactions:
                        amount = int(txs['value'],16)/1e18
                        timestamp = int(txs['timestamp'],16)
                        timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
                        t = {
                            "timestamp": timestamp,
                            "shard": shard,
                            "block": i,
                            "volumn": amount,
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