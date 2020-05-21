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

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'address'))

def getLatestHeader(shard) -> dict:
    url = endpoint[shard]
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "hmy_latestHeader",
        "params": ['latest'],
        "id": 1
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request('POST', url, headers=headers, data=payload, allow_redirects=False, timeout=30)
    try:
        returned = json.loads(response.content)["result"]
        return returned
    except Exception:  # Catch all to not halt
        logger.info(f"\n[!!!] Failed to json load latestHeader. Content: {response.content}\n")


def getBlockByNumber(shard, block, logger):
    url = endpoint[shard]
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "hmyv2_getBlockByNumber",
        "params": [
            block, 
            {"fullTx":True,"inclTx": True, "withSigners":False,"InclStaking":False}
        ],
        "id": 1
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request('POST', url, headers=headers, data=payload, allow_redirects=False, timeout=30)
    try:
        returned = json.loads(response.content)["result"]
        return returned
    except Exception:  # Catch all to not halt
        t= {
            'block-num': block,
            'reason': f"Failed to json load block {block}. Content: {response.content}"
        }
        logger.info(json.dumps(t))
        print(f"\n[!!!] Failed to json load block {block}. Content: {response.content}\n")


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

    pkl_file = path.join(data,'address_{}.pickle'.format(network))

    if path.exists(pkl_file):
        with open(pkl_file, 'rb') as f:
            address = pickle.load(f)
    else:      
        filename = path.join(data, 'fn_addresses.csv')
        fn_addr = pd.read_csv(filename, header = None, names = ['address', 'shard'])
        address = set(fn_addr['address'].tolist())
        
    shard_info = path.join(data,'shard_info_{}.pickle'.format(network))
    if path.exists(shard_info):
        with open(shard_info, 'rb') as f:
            prev = pickle.load(f)
    else:
        prev = {0:1, 1:1, 2:1, 3:1}

    while True:
        addr_length = len(address)
        curr = defaultdict(int)
        for shard in range(len(endpoint)):
            latest = getLatestHeader(shard)
            if latest == None:
                curr[shard] = prev[shard]
            else:
                curr[shard] = latest['blockNumber']  
        total = 0
        for shard in range(len(endpoint)):
            length = curr[shard] - prev[shard]
            total += length

        q = Queue()
        def collect_data(q): 
            while not q.empty():
                global address
                i, shard = q.get()
                res = getBlockByNumber(shard, i, logger)
                if res != None:
                    transactions = res['transactions']
                    if transactions:
                        for txs in transactions:
                            if (txs['from'] not in address) and (re.match('one1', txs['from']) != None):
                                address.add(txs['from'])
                                
                            if (txs['to'] not in address) and (re.match('one1', txs['to']) != None):
                                address.add(txs['to'])                                
                    if i % 1000 == 1:
                        timestamp = res['timestamp']
                        timestamp = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d %H:%M:%S')
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
        if len(address) != addr_length:
            logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} pickle file updated")
            with open(pkl_file, 'wb') as f:
                pickle.dump(address, f)
        prev = copy.deepcopy(curr)  
        
        with open(shard_info, 'wb') as f:
            pickle.dump(prev, f)
        time.sleep(30)