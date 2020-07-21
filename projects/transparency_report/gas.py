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
logs = path.abspath(path.join(base, 'transaction_data'))

def new_log():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("txs_data")
    logger.setLevel(logging.INFO)
    filename = path.join(logs, "old_txs_data.log")
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
     
    prev = {0: 0, 1:0, 2:0, 3:0}
    curr = defaultdict(int)
    # get the number of threads
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
            i, shard = q.get()
            res = blockchain.get_block_by_number(i, endpoint=endpoint[shard], include_full_tx=True)
            if res != None:
                transactions = res['transactions']
                for txs in transactions:
                    gas = int(txs['gas'],16)
                    gasPrice = int(txs['gasPrice'],16)
                    amount = int(txs['value'],16)/1e18
                    timestamp = int(txs['timestamp'],16)
                    timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
                    t = {
                        "timestamp": timestamp,
                        "shard": shard,
                        "block": i,
                        "gas": gas,
                        "gasPrice": gasPrice,
                        "volume": amount,
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