#!/usr/bin/env python
# coding: utf-8

import json
import requests
import pandas as pd
import numpy as np
import os
from os import path
from datetime import datetime
from threading import Thread
import logging
from collections import defaultdict
import gspread
import pickle
import argparse
import pyhmy 
from pyhmy import rpc
import time 
from queue import Queue

def new_log(network):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ONE_holder")
    logger.setLevel(logging.INFO)
    track_file = path.join(log_dir, "tracking_FN_{}.log".format(network))
    if path.exists(track_file):
        os.remove(track_file)
    file_handler = logging.FileHandler(track_file)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json; charset=utf8'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
    except requests.exceptions.ConnectionError as e:
        print("Error: connection error")
        time.sleep(5)
        return None
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        r.json()
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    return r.json()
    
def getBalance(shard, address) -> int:
    url = endpoint[shard]
    method = 'hmyv2_getBalance'
    params = [address]
    return get_information(url, method, params)

def getBalanceByBlockNumber(shard, address, block):
    url = endpoint[shard]
    method = 'hmy_getBalanceByBlockNumber'
    params = [address, hex(block)]
    return get_information(url, method, params)

def getTransactionsCount(shard, address) -> int:
    url = endpoint[shard]
    method = 'hmy_getTransactionsCount'
    params = [address, 'ALL']
    return get_information(url, method, params)


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

    base = path.dirname(path.realpath(__file__))
    addr_dir = path.abspath(path.join(base, 'address'))
    log_dir = path.abspath(path.join(base, 'logs'))
    csv_dir = path.abspath(path.join(base, 'csv/{}'.format(network)))
    
    folder = [log_dir, csv_dir, addr_dir]
    for f in folder:
        if not path.exists(f):
            try:
                os.makedirs(f)
            except:
                print("Could not make data directory")
                exit(1)
    
    logger = new_log(network)
    
    
    filename = path.join(addr_dir, 'fn_addresses.csv')
    fn_addr = pd.read_csv(filename, header = None, names = ['address', 'shard'])

    address = fn_addr['address'].tolist()
    thread_lst = defaultdict(list)
    for i in range(len(address)):
        thread_lst[i%100].append(i)

    block_num = {0:3375104, 1:3286736, 2:3326152, 3:3313571}
    time_dict = {0: "2020_05_16_15:08:52", 1: "2020_05_16_15:08:53", 2: "2020_05_16_15:08:56", 3:"2020_05_16_15:08:53"} 
    def collect_data(x):
        for i in thread_lst[x]: 
            balance = 0
            stake = 0
            txs_sum = 0
            hash_set = set()
            addr = address[i]
            for shard in range(len(endpoint)):
                fail = True
                retry = False
                res = 0
                while fail:
                    try:
                        res = rpc.account.get_balance_by_block(addr, block_num[shard], endpoint[shard])
                        fail = False
                        if retry:
                            logger.info("retry succeed")
                    except:
                        logger.info(f"cannot get balance for address:{addr}, shard: {shard}, error: {res}")
                        time.sleep(2)
                        retry = True
                        pass
                    if res:
                        balance += res/1e18
                    transactions = rpc.account.get_transaction_history(addr, page=0, page_size=10000, include_full_tx=True, tx_type='ALL',order='ASC', endpoint=endpoint[shard])
                    for txs in transactions:
                        txs_hash = txs['hash']
                        if txs_hash in hash_set:
                            continue
                        else:
                            hash_set.add(txs_hash)
                        timestamp = int(txs['timestamp'],16)
                        str_time = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d_%H:%M:%S')
                        if str_time > time_dict[shard]:
                            continue
                        if txs['from'] == addr:
                            txs_sum -= int(txs['value'],16)/1e18
                        if txs['to'] == addr:
                            txs_sum += int(txs['value'],16)/1e18
            staking_txs = rpc.account.get_staking_transaction_history(addr, page=0, page_size=10000, include_full_tx=True, tx_type='ALL', order='ASC', endpoint=endpoint[0])
            for s in staking_txs:
                str_time = datetime.fromtimestamp(s['timestamp']).strftime('%Y_%m_%d_%H:%M:%S')
                if str_time > time_dict[0]:
                    continue
                if s['type'] == 'Delegate':
                    stake += s['msg']['amount']/1e18
                elif s['type'] == 'Undelegate':
                    stake -= s['msg']['amount']/1e18
                elif s['type'] == 'CreateValidator':
                    stake += s['msg']['amount']/1e18
            net_balance = balance - txs_sum + stake
                    
            t = {
                "address": addr,
                "curr-balance": balance,
                "txs-sum": txs_sum,
                "total-stake": stake,
                "net-balance": net_balance
            }
            logger.info(json.dumps(t))


    threads = []
    for x in range(100):
        threads.append(Thread(target = collect_data, args = [x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


    
    file_name = path.join(log_dir, "tracking_FN_{}.log".format(network))
    result = []
    with open(file_name, errors='ignore') as f:
        for line in f.readlines():
            try: 
                result.append(json.loads(line))
            except:
                print('bad json: ', line)
    df = pd.DataFrame(result)
    df.sort_values(by=['net-balance'], ascending=False, inplace = True) 
    
    df = df.join(fn_addr.set_index('address'), on = 'address')
    df.reset_index(inplace = True, drop = True)
    csv_name = "{}_FN_{}_tracker.csv".format(network, datetime.now().strftime("%Y_%m_%d %H:%M:%S"))
    df.to_csv(path.join(csv_dir, csv_name))
                                
    json_file = path.join(base, 'credential/jsonFileFromGoogle.json')
    gc = gspread.service_account(json_file)
    sh = gc.open("harmony-{}-tracker".format(network))
    worksheet = sh.worksheet("FN-tracker")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())