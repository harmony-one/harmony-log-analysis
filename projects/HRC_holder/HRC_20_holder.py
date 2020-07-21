#!/usr/bin/env python
# coding: utf-8

import pyhmy 
from pyhmy import (
    blockchain,
    rpc,
    account,
    staking,
    cli
)
import os
import re
from datetime import datetime
from os import path
import json
import pandas as pd
from collections import defaultdict
import requests
from threading import Thread
import time
import argparse
import logging
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

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
    

def getTransactionsHistory(shard, address, page, size):
    url = endpoint[shard]
    method = 'hmyv2_getTransactionsHistory'
    params = [{
        "address": address,
        "pageIndex": page,
        "pageSize": size,
        "fullTx": True,
        "txType": "ALL",
        "order": "ASC"
    }]
    return get_information(url, method, params)['result']['transactions']


def download_cli(path):
    env = cli.download()
    cli.environment.update(env)
    path = os.getcwd() + "/bin/hmy"
    cli.set_binary(path)


base = path.dirname(path.realpath(__file__))
addr_dir = path.abspath(path.join(base, 'address'))
log_dir = path.abspath(path.join(base, 'logs'))
json_dir = path.abspath(path.join(base, 'credential'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas')
    parser.add_argument('--address', required = True, help = 'HRC20 address to query from, seperated by commas')
    parser.add_argument('--name', required = True, help = 'HRC20 name to query from, seperated by commas')
    args = parser.parse_args()
    endpoint = []
    if args.endpoints:
        endpoint = [x.strip() for x in args.endpoints.strip().split(',')]        
    else:
        print('List of endpoints is required.')
        exit(1)
    if args.address:
        address = [x.strip() for x in args.address.strip().split(',')]        
    else:
        print('Address is required.')
        exit(1)
    if args.name:
        name = [x.strip() for x in args.name.strip().split(',')]        
    else:
        print('Name is required.')
        exit(1)
        
    length = len(address)
    name_dict = dict(zip(list(range(length)), name))
    addr_dict = dict(zip(list(range(length)), address))
    addr_to_name = dict(zip(address, name))
    data = [addr_dir, log_dir, json_dir]
    for d in data:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make address directory")
                exit(1)
        
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HRC_holder")
    logger.setLevel(logging.INFO)
    filename = "{}/get_HRC_address.log".format(log_dir)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    cli_path = os.getcwd() + "/bin/hmy"       
    download_cli(cli_path)
    pyhmy_version = cli.get_version()
    print(f"CLI Version: {pyhmy_version}")
    version_str = re.search('version v.*-', pyhmy_version).group(0).split('-')[0].replace("version v", "")
    assert int(version_str) >= 321
    
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})
    ref = db.reference('HRC-holder')
    ref.child('address').set(addr_dict)
    ref.child('name').set(name_dict)
    
    pkl_file = path.join(addr_dir,'address_HRC.pkl')
    if path.exists(pkl_file):
        # restart from last records
        with open(pkl_file, 'rb') as f:
            addr_set = pickle.load(f)
            if len(address) != len(addr_set):
                for i in address:
                    if i not in addr_set:
                        addr_set[i] = set()
                        sub_ref = ref.child(i)
                        sub_ref.child('name').set(addr_to_name[i])
                    print(f"add new address {i} to address_HRC")
    else: 
        addr_set = dict.fromkeys(address, set())
        
    page_info = path.join(addr_dir,'txs_page_info.pkl')
    if path.exists(page_info):
        with open(page_info, 'rb') as f:
            prev = pickle.load(f)
            if len(address) != len(prev):
                for i in address:
                    if i not in prev:
                        info = {0:0, 1:0, 2:0, 3:0}
                        prev[i] = info
                    print(f"add new address {i} to txs page info")
    else:
        info = {0:0, 1:0, 2:0, 3:0}
        prev = dict.fromkeys(address,info)
    

    while True:  
        transactions = defaultdict(list)
        txs_dict = defaultdict(int)
        for idx in range(len(addr_dict)):  
            addr = addr_dict[idx]
            addr_length = len(addr_set[addr])
            for shard in range(len(endpoint)):
                prev_count = prev[addr][shard]
                page = max(0, (prev_count-1))//1000
                size = max(0, (prev_count-1))%1000+1
                if size == 1000:
                    page += 1
                    size = 0
                res = getTransactionsHistory(shard, addr, page, 1000)
                if len(res) != 0 and len(res) != size:
                    transactions[addr].extend(res[size:len(res)])
                    while len(res) == 1000:
                        page += 1
                        res = getTransactionsHistory(shard, addr, page, 1000)
                        transactions[addr].extend(res[0:len(res)])
                    prev[addr][shard] = page*1000+len(res)
                    with open(page_info, 'wb') as f:
                        pickle.dump(prev, f)
                    logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} page info for {addr} shard {shard} updates: {prev[addr][shard]}")
                txs_dict[idx] += prev[addr][shard]
            thread_lst = defaultdict(list)
            total = min(50, len(transactions[addr]))
            logger.info(f"address {addr}, total processing thread, {total}")
            for i in range(len(transactions[addr])):
                thread_lst[i%total].append(i)
            
            def collect_data(x):
                for i in thread_lst[x]: 
                    global addr_set
                    txs = transactions[addr][i]
                    data = txs['input']
                    msg_type = data[:10]
                    if msg_type != '0xa9059cbb':
                        continue
                    addr_bytes = data[10:74]
                    addr_hrc = cli.single_call("hmy utility addr-to-bech32 {}".format(addr_bytes)).strip("\n")
                    if addr_hrc not in addr_set[addr]:
                        addr_set[addr].add(addr_hrc)
                        logger.info(f"{addr_hrc} added")

            threads = []
            for x in range(total):
                threads.append(Thread(target = collect_data, args = [x]))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            time.sleep(30)
            
            sub_ref = ref.child(addr)
            if len(addr_set[addr]) != addr_length:
                logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} hrc_address {addr} updated")
                with open(pkl_file, 'wb') as f:
                    pickle.dump(addr_set, f)
                addr_list = defaultdict(list)
                addr_list[addr] = list(addr_set[addr])
                length = len(addr_set[addr])
                sub_ref.child('address').set(dict(zip(list(range(length)), addr_set[addr])))
                sub_ref.child('length').set(length)
                
        
        ref.child('transactions').set(txs_dict)
        print("txs update")
        time.sleep(300)