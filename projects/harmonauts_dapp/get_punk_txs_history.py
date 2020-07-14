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
    

def getTransactionsHistory(endpoint, address, page, size):
    url = endpoint
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
# store the firebase private key json file
json_dir = "/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/credential"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoints', required = True, help = 'Endpoints to query from, seperated by commas')
    parser.add_argument('--address', required = True, help = 'HRC address to query from, seperated by commas')
    args = parser.parse_args()
    if args.endpoints:
        endpoint = args.endpoints.strip()       
    else:
        print('List of endpoints is required.')
        exit(1)
    if args.address:
        addr = args.address.strip()   
    else:
        print('Address is required.')
        exit(1)
        
    data = [addr_dir, log_dir]
    for d in data:
        if not path.exists(d):
            try:
                os.mkdir(d)
            except:
                print("Could not make address directory")
                exit(1)
        
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Punk_txs_history")
    logger.setLevel(logging.INFO)
    filename = "{}/get_punk_txs.log".format(log_dir)
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
    
    # record the txs history
    pkl_file = path.join(addr_dir,'punk_txs.pkl')
    if path.exists(pkl_file):
        # restart from last records
        with open(pkl_file, 'rb') as f:
            txs_history = pickle.load(f)
          
    else: 
        txs_history = defaultdict(dict)
    
    # record the latest txs page, only need to query from the latest page, speed up query process
    page_info = path.join(addr_dir,'punk_txs_page.pkl')
    if path.exists(page_info):
        with open(page_info, 'rb') as f:
            prev = pickle.load(f)
    else:
        prev = 0
        
    # avoid duplicated txs record
    txs_hash_info = path.join(addr_dir,'punk_txs_hash.pkl')
    if path.exists(txs_hash_info):
        with open(txs_hash_info, 'rb') as f:
            txs_hash_set = pickle.load(f)
    else:
        txs_hash_set = set()
    
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})
    
    while True:  
        len_dict = defaultdict(int)
        for key, value in txs_history.items():
            len_dict[key] = len(value)
        transactions = []
        prev_count = prev
        page = max(0, (prev_count-1))//1000
        size = max(0, (prev_count-1))%1000+1
        res = getTransactionsHistory(endpoint, addr, page, 1000)
        if prev_count == 0:
            transactions = res
        elif len(res) != 0 and len(res) != size:
            transactions.extend(res[size:len(res)])
            while len(res) == 1000:
                page += 1
                res = getTransactionsHistory(endpoint, addr, page, 1000)
                transactions[addr].extend(res[0:len(res)])
        prev = page*1000+len(res)
        if prev != prev_count:
            with open(page_info, 'wb') as f:
                pickle.dump(prev, f)
            logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} page info updates: {prev}")

        thread_lst = defaultdict(list)
        total = min(50, len(transactions))
        for i in range(len(transactions)):
            thread_lst[i%total].append(i)

        def collect_data(x):
            for i in thread_lst[x]: 
                global txs_history, txs_hash_set
                txs = transactions[i]
                txs_hash = txs['hash']
                if txs_hash in txs_hash_set:
                    continue
                else:
                    txs_hash_set.add(txs_hash)
                timestamp = txs['timestamp']
                data = txs['input']
                msg_type = data[:10]
                if msg_type == '0xa75a9049':
                    addr_bytes = data[10:74]
                    addr_hrc = cli.single_call("hmy utility addr-to-bech32 {}".format(addr_bytes)).strip("\n")
                    punkIndex = int(data[-64:],16)
                    log = {
                        "Type": "Set-Initial-Owner",
                        "From": "",
                        "To": addr_hrc,
                        "Amount": "",
                        "Txn": timestamp
                    }
                    
                elif msg_type == "0xc81d1d5b":
                    punkIndex = int(data[-64:],16)
                    from_addr = txs['from']
                    log = {
                        "Type": "Claimed",
                        "From": "",
                        "To": from_addr,
                        "Amount":"",
                        "Txn": timestamp
                    }  
                elif msg_type == "0xc44193c3":
                    punkIndex = int(data[10:74],16)
                    amount = int(data[-64:],16)/1e18
                    from_addr = txs['from']
                    log = {
                        "Type": "Offered",
                        "From": from_addr,
                        "To": "",
                        "Amount": amount,
                        "Txn": timestamp
                    }
                elif msg_type == "0x8264fe98":
                    punkIndex = int(data[-64:],16)
                    to_addr = txs['from']
                    amount = txs['value']/1e18
                    if amount == 0:
                        log = {
                        "Type": "Failed Buying",
                        "From": "",
                        "To": to_addr,
                        "Amount": amount,
                        "Txn": timestamp
                    }
                    else:   
                        log = {
                            "Type": "Sold",
                            "From": "",
                            "To": to_addr,
                            "Amount": amount,
                            "Txn": timestamp
                        }
                elif msg_type == "0x8b72a2ec":
                    addr_bytes = data[10:74]
                    addr_hrc = cli.single_call("hmy utility addr-to-bech32 {}".format(addr_bytes)).strip("\n")
                    punkIndex = int(data[-64:],16)
                    log = {
                        "Type": "Transfered",
                        "From": from_addr,
                        "To": "",
                        "Amount": "",
                        "Txn": timestamp
                    }
                elif msg_type == "0x091dbfd2":
                    punkIndex = int(data[-64:],16)
                    from_addr = txs['from']
                    amount = txs['value']/1e18
                    log = {
                        "Type": "Bid",
                        "From": from_addr,
                        "To": "",
                        "Amount": amount,
                        "Txn": timestamp
                    }
                elif msg_type == '0x23165b75':
                    punkIndex = int(data[10:74],16)
                    from_addr = txs['from']
                    amount = int(data[-64:],16)/1e18
                    log = {
                        "Type": "Accept Bid",
                        "From": from_addr,
                        "To": "",
                        "Amount": amount,
                        "Txn": timestamp
                    }
                else:
                    continue
                index = len(txs_history[punkIndex])
                txs_history[punkIndex][index] = log

        threads = []
        for x in range(total):
            threads.append(Thread(target = collect_data, args = [x]))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        ref = db.reference('harmony-punk')
#         ref.set(txs_history)
#         logger.info(f"update in firebase")
        flag = False
        for key, value in txs_history.items():
            new_length = len(value)
            old_length = len_dict[key]
            if new_length != old_length:
                addr_ref = ref.child(str(key))
                if addr_ref.get():
                    addr_ref.update(value)
                else:
                    addr_ref.set(value)
                flag = True
                logger.info(f"update in firebase")
        if flag:
            logger.info(f"{datetime.now().strftime('%Y_%m_%d %H:%M:%S')} updated txs history")
            with open(pkl_file, 'wb') as f:
                pickle.dump(txs_history, f)
            with open(txs_hash_info, 'wb') as f:
                pickle.dump(txs_hash_set, f)
        
        time.sleep(10)