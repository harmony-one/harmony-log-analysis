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
data = path.abspath(path.join(base, 'address'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas')
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
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ONE_holder")
    logger.setLevel(logging.INFO)
    filename = "./logs/get_{}_address.log".format(network)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make address directory")
            exit(1)

    addr_file = path.join(data,'address_{}.txt'.format(network))
    if path.exists(addr_file):
        # restart from last records
        address = set()
        with open(addr_file, 'r') as f:
            for line in f:
                curr = line[:-1]
                address.add(curr)       
    else: 
        # first time setup: since some foundational nodes doesn't have txs history
        filename = path.join(data, 'fn_addresses.csv')
        fn_addr = pd.read_csv(filename, header = None, names = ['address', 'shard'])
        address = set(fn_addr['address'].tolist())
        
    shard_info = path.join(data,'shard_info_{}.txt'.format(network))
    if path.exists(shard_info):
        with open(shard_info, 'r') as f:
            prev = json.load(f, object_hook=lambda d: {int(k): v for k, v in d.items()})
    else:
        prev = {0:1, 1:1, 2:1, 3:1}

    while True:
        addr_length = len(address)
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
                global address
                i, shard = q.get()
                fail = True
                while fail:
                    try:
                        res = blockchain.get_block_by_number(i, endpoint[shard], include_full_tx=True)
                        fail = False
                    except rpc.exceptions.RequestsTimeoutError:
                        time.sleep(20)
                        pass
                if res:
                    transactions = res['transactions']
                    if transactions:
                        for txs in transactions:
                            if (txs['from'] not in address) and (re.match('one1', txs['from']) != None):
                                address.add(txs['from'])
                                
                            if (txs['to'] not in address) and (re.match('one1', txs['to']) != None):
                                address.add(txs['to'])                                
                    if i % 1000 == 1:
                        timestamp = res['timestamp']
                        timestamp = datetime.fromtimestamp(int(timestamp,16)).strftime('%Y_%m_%d %H:%M:%S')
                        t = {
                            "block": i,
                            "shard": shard,
                            "timestamp": timestamp
                        }
                        logger.info(json.dumps(t))
                q.task_done()

        for shard in range(len(endpoint)):
            for x in range(prev[shard], curr[shard]):
                q.put((x,shard))
                
        num_threads = min(100, total)
        for i in range(num_threads):
            worker = Thread(target = collect_data, args = (q,))
            worker.setDaemon(True)
            worker.start()

        q.join()
        
        # save data if we have new address
        if len(address) != addr_length:
            logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} address file updated")
            with open(addr_file, 'w') as f:
                for i in address:
                    f.write('%s\n' % i)
        
        # deep copy dictionary
        prev = copy.deepcopy(curr)  
        # to quickly consume when any request error happen
        with open(shard_info, 'w') as f:
            json.dump(prev, f)
        time.sleep(30)