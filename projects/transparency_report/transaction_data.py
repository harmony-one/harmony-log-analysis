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

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', required = True, help = 'File name for data log')
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas.')
    parser.add_argument('--sleep', default = 4, type = int, help = 'Sleep timer')
    args = parser.parse_args()
    endpoint = []
    if args.endpoints:
        endpoint = [x.strip() for x in args.endpoints.strip().split(',')]        
    else:
        print('List of endpoints is required.')
        exit(1)
        
    directory = [logs]
    for d in directory:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make directory")
                exit(1)
            
    # set up logger
    logger = logging.getLogger("transaction_data")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(path.join(logs, args.output_file))
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
     
    try:
        while True:
            def collect_data(shard):
                latest = blockchain.get_latest_header(endpoint[shard])
                if latest:
                    i = latest['blockNumber']
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
            threads = []
            for x in range(len(endpoint)):
                threads.append(Thread(target = collect_data, args = [x]))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            time.sleep(args.sleep)
    except KeyboardInterrupt:
        pass