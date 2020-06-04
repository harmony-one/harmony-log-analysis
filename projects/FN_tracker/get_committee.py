#!/usr/bin/env python
# coding: utf-8

import requests
import json
from collections import defaultdict
import logging
from datetime import datetime
import os
from os import path
import time
import argparse
import pickle 
from threading import Thread
import pyhmy
from pyhmy import rpc

base = path.dirname(path.realpath(__file__))
log_dir = path.abspath(path.join(base, 'logs'))
pkl_dir = path.abspath(path.join(base, 'pickle'))
mainnetEpochBlock1 = 344064
blocksPerEpoch = 16384

def new_log(date, network):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("committee")
    logger.setLevel(logging.INFO)
    filename = "committee_{}_{}.log".format(network, date)
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
    
    directory = [log_dir, pkl_dir]
    for i in directory:
        if not path.exists(i):
            try:
                os.mkdir(i)
            except:
                print("Could not make data directory")
                exit(1)
      
    count_file = path.join(pkl_dir,'committee_count_{}.pkl'.format(network))
    if path.exists(count_file):
        with open(count_file, 'rb') as f:
            count = pickle.load(f)
    else:  
        count = defaultdict(dict)
        for shard in range(len(endpoint)): 
            address = rpc.blockchain.get_validators(0,endpoint[shard])['validators']
            for i in address:
                addr = i['address']
                if addr == 'one1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqquzw7vz':
                    continue
                count[shard][addr] = mainnetEpochBlock1 - 1

    date = datetime.utcnow().strftime('%Y_%m_%d')
    logger = new_log(date, network)
    shard_info = path.join(pkl_dir,'epoch_{}.pickle'.format(network))
    if path.exists(shard_info):
        with open(shard_info, 'rb') as f:
            curr = pickle.load(f)
    else:
        curr = 1
        
    target = 150
    while curr <= target:
        def collect_data(shard):
            fail = True
            address = []
            while fail:
                try:
                    address = rpc.blockchain.get_validators(curr,endpoint[shard])['validators']
                    fail = False
                except rpc.exceptions.RequestsTimeoutError:
                    time.sleep(10)
                    pass
            if address:
                for i in address:
                    addr = i['address']
                    if addr == 'one1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqquzw7vz':
                        continue
                    if addr not in count[shard]:
                        count[shard][addr] = blocksPerEpoch
                    else:
                        count[shard][addr] += blocksPerEpoch    
            else:
                logger.info(f"\n[!] WARNING epoch {epoch} had a null response: {address}\n")
        
        threads = []       
        for x in range(len(endpoint)):
            threads.append(Thread(target = collect_data, args = [x]))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        with open(count_file, 'wb') as f:
            pickle.dump(count, f)
            
        with open(shard_info, 'wb') as f:
            pickle.dump(curr, f)
        
        logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} pickle file updated, epoch: {curr}")
        
        curr += 1
    
    for shard in range(len(endpoint)):
        address = rpc.blockchain.get_validators(151,endpoint[shard])['validators']
        if address:
            for i in address:
                addr = i['address']
                if addr == 'one1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqquzw7vz':
                    continue
                count[shard][addr] += blocksPerEpoch * (185-151+1)  
       
    with open(count_file, 'wb') as f:
        pickle.dump(count, f)
            
    with open(shard_info, 'wb') as f:
        pickle.dump(curr, f)
        
    logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} finished updating pickle file, from epoch 151 to 185")

        

        
        

