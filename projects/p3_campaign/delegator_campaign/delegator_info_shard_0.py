#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import os
from os import path
import requests
from collections import defaultdict
from threading import Thread
import pyhmy
from pyhmy import rpc

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:ßs
        content = json.loads(r.content)
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    if "error" in content:
        print("Error: The method does not exist/is not available")
        return None
    else:
        return content['result']

def getAllValidatorInformationByBlockNumber(block):
    url = 'http://localhost:9500'
    method = 'hmy_getAllValidatorInformationByBlockNumber'
    params = [-1, hex(block)]
    return get_information(url, method, params)

if __name__ == "__main__":

    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'csv'))
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make csv directory")
            exit(1)

    print("-- Start Data Processing --")
    validator_infos = getAllValidatorInformationByBlockNumber(88515)
    print(f"Current Epoch number: 196, Block number: 88515")
    del_reward = defaultdict(float)
    del_stake = defaultdict(float)
    undel = defaultdict(float)
    val_address = []

    # get the accumualted reward in current block
    for info in validator_infos:
        address = info['validator']['address']
        val_address.append(address)
        epoch = info['validator']['last-epoch-in-committee']
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            del_reward[del_address] += reward
            amount = d['amount']/1e18
            del_stake[del_address] += amount
            for u in d['undelegations']:
                if epoch - u['epoch'] <= 7:
                    undel[del_address] += u['amount']/1e18

    del_address = set(del_reward.keys()) - set(val_address)
    balance = defaultdict(float)
    txs_sum = defaultdict(float)
    address_lst = list(del_address)
#     address_lst.remove("one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur")
    thread_lst = defaultdict(list)
    for i in range(len(address_lst)):
        thread_lst[i%25].append(i)
    def collect_data(x):
        global balance
        for i in thread_lst[x]:
            addr = address_lst[i]
            res = rpc.account.get_balance_by_block(addr,88515)
            if res != None:
                balance[addr] += res/1e18

    threads = []
    for x in range(25):
        threads.append(Thread(target = collect_data, args = [x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    thread_lst = defaultdict(list)
    for i in range(88515):
        thread_lst[i%100].append(i)

    def collect_data(x):
        global txs_sum
        for i in thread_lst[x]:
            transactions = rpc.blockchain.get_block_by_number(i, include_full_tx=True)['transactions']
            for txs in transactions:
                if txs['from'] in address_lst:
                    addr = txs['from']
                    txs_sum[addr] -= int(txs['value'],16)/1e18
                if txs['to'] in address_lst:
                    addr = txs['to']
                    txs_sum[addr] += int(txs['value'],16)/1e18
    threads = []
    for x in range(100):
        threads.append(Thread(target = collect_data, args = [x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance_shard_0'])
    txs_sum_df = pd.DataFrame(txs_sum.items(), columns=['address', 'txs_sum_shard_0'])

    new_del_reward = dict()
    new_del_stake = dict()
    new_undel = dict()
    for k,v in del_reward.items():
        if k in address_lst:
            new_del_reward[k] = v
            new_del_stake[k] = del_stake[k]
            new_undel[k] = undel[k]
    reward_df = pd.DataFrame(new_del_reward.items(), columns=['address', 'current-reward'])
    stake_df = pd.DataFrame(new_del_stake.items(), columns=['address', 'total-stake'])
    undel_df = pd.DataFrame(new_undel.items(), columns=['address', 'pending-undelegation'])
    df = reward_df.join(stake_df.set_index('address'), on = 'address')
    df = df.join(balance_df.set_index('address'), on = 'address')
    df = df.join(undel_df.set_index('address'), on = 'address')
    df = df.join(txs_sum_df.set_index('address'), on = 'address')

    print("-- Save csv files to ./csv/shard_0_delegator.csv --")
    df.to_csv(path.join(data, 'shard_0_delegator.csv'))

