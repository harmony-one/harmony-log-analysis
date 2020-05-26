#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import os
from os import path
import requests
import csv
import re
from collections import defaultdict
import datetime
from threading import Thread
from queue import Queue
import time

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        content = json.loads(r.content)
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    if "error" in content:
        print("Error: The method does not exist/is not available")
        return None
    else:
        return content['result']

def getAllValidatorInformation():
    url = 'https://api.s0.t.hmny.io/'
    method = 'hmy_getAllValidatorInformation'
    params = [-1]
    return get_information(url, method, params)

def getBalance(shard, address):
    url = endpoint[shard]
    method = "hmy_getBalance"
    params = [address, "latest"]
    res = get_information(url, method, params)
    if res != None:
        return int(res,16)/1e18

def getTransactionHistory(shard, address):
    url = endpoint[shard]
    method = "hmyv2_getTransactionsHistory"
    params = [{
        "address": address,
        "fullTx": True,
        "pageIndex": 0,
        "pageSize": 100000,
        "txType": "ALL",
        "order": "ASC"
    }]
    res = get_information(url, method, params)
    if res != None:
        return res['transactions']

def getTransactionCount(shard, address):
    url = endpoint[shard]
    method = "hmy_getTransactionCount"
    params = [address, 'latest']
    res = get_information(url, method, params)
    if res != None:
        return int(res,16)
    
def getTransactionsCount(shard, address) -> int:
    url = endpoint[shard]
    method = 'hmy_getTransactionsCount'
    params = [address, 'ALL']
    res = get_information(url, method, params)
    if res != None:
        return res

def getStakingTransactionCount(address):
    url = 'https://api.s0.t.hmny.io/'
    method = 'hmy_getStakingTransactionsCount'
    params = [address, 'ALL']
    return get_information(url, method, params)

def getEpoch():
    url = 'https://api.s0.t.hmny.io/'
    method = "hmy_getEpoch"
    params = []
    epoch = get_information(url, method, params)
    return int(epoch, 16)

def getBlockNumber():
    url = 'https://api.s0.t.hmny.io/'
    method = "hmy_blockNumber"
    params = []
    num = get_information(url, method, params)
    return int(num, 16)

def read_csv(csv_file) -> (list):
    encoding = 'utf-8'
    r = requests.get(csv_file)
    s = [x.decode(encoding) for x in r.content.splitlines()]
    v = []
    for line in csv.reader(s):
        address = line[3].strip()
        if re.match('one1', address) != None:
            v.append(address)
    return v


if __name__ == "__main__":  
    
    endpoint = ['https://api.s0.t.hmny.io/', 'https://api.s1.t.hmny.io/', 'https://api.s2.t.hmny.io/', 'https://api.s3.t.hmny.io/']
    
    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'csv'))
    data = path.join(data, 'mainnet_delegator')
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make csv directory")
            exit(1)
  
    print("-- Start Data Processing --")
    validator_infos = getAllValidatorInformation()
    epoch = getEpoch()
    block = getBlockNumber()
    print(f"Current Epoch number: {epoch}, Block number: {block}")
    del_reward = defaultdict(float)
    del_stake = defaultdict(float)
    val_address = []
    # get the accumualted reward in current block
    for info in validator_infos:
        address = info['validator']['address']
        val_address.append(address)
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            del_reward[del_address] += reward
            amount = d['amount']/1e18
            del_stake[del_address] += amount

    del_address = set(del_reward.keys()) - set(val_address)
    balance = defaultdict(float)
    staking_transaction = defaultdict(int)
    normal_transaction = defaultdict(int)
    address_lst = list(del_address)
    thread_lst = defaultdict(list)
    for i in range(len(address_lst)):
        thread_lst[i%50].append(i)
    def collect_data(shard, x):
        global staking_transaction, normal_transaction, balance, txs_sum
        for i in thread_lst[x]:
            addr = address_lst[i]
            if shard == 0:
                staking_transaction[addr] = getStakingTransactionCount(addr)
            res = getBalance(shard, addr)
            if res != None:
                balance[addr] += res
                count = getTransactionsCount(shard, addr)
                if count != None:
                    normal_transaction[addr] += count

    threads = []
    for x in range(50):
        for shard in range(len(endpoint)):
            threads.append(Thread(target = collect_data, args = [shard, x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    print("-- Finish Data Processing --")
    epoch = getEpoch()
    block = getBlockNumber()
    print(f"Current Epoch number: {epoch}, Block number: {block}")
    
    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance'])
    staking_transaction_df = pd.DataFrame(staking_transaction.items(), columns = ['address', 'staking-transaction-count'])
    normal_transaction_df = pd.DataFrame(normal_transaction.items(), columns = ['address', 'normal-transaction-count'])
    
    new_del_reward = dict()
    new_del_stake = dict()
    for k,v in del_reward.items():
        if k in address_lst:
            new_del_reward[k] = v
            new_del_stake[k] = del_stake[k]

    reward_df = pd.DataFrame(new_del_reward.items(), columns=['address', 'current-reward'])
    stake_df = pd.DataFrame(new_del_stake.items(), columns=['address', 'total-stake'])
    df = reward_df.join(stake_df.set_index('address'), on = 'address')
    df = df.join(balance_df.set_index('address'), on = 'address')
    df = df.join(staking_transaction_df.set_index('address'), on = 'address')
    df = df.join(normal_transaction_df.set_index('address'), on = 'address')
    time = datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S") 

    print("-- Save csv files to ./csv/mainnet_delegator/{:s}_delegator.csv --".format(time))
    df.to_csv(path.join(data, '{:s}_delegator.csv'.format(time)))
