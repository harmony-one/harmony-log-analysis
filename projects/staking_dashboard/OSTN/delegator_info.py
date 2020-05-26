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

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    content = json.loads(r.content)
    return content

def getAllValidatorInformation() -> dict:
    url = 'https://api.s0.os.hmny.io/'
    method = 'hmy_getAllValidatorInformation'
    params = [-1]
    return get_information(url, method, params)['result']

def getBalance(address) -> int:
    url = 'https://api.s0.os.hmny.io/'
    method = "hmy_getBalance"
    params = [address, "latest"]
    return int(get_information(url, method, params)['result'],16)

def getTransactionsCount(shard, address) -> int:
    url = endpoint[shard]
    method = "hmy_getTransactionsCount"
    params = [address, 'ALL']
    return get_information(url, method, params)['result']

def getTransactionCount(shard, address) -> int:
    url = endpoint[shard]
    method = "hmy_getTransactionCount"
    params = [address, 'latest']
    return int(get_information(url, method, params)['result'],16)

def getStakingTransactionCount(address) -> int:
    url = 'https://api.s0.os.hmny.io/'
    method = 'hmy_getStakingTransactionsCount'
    params = [address, 'ALL']
    return get_information(url, method, params)['result']

def getEpoch() -> int:
    url = 'https://api.s0.os.hmny.io/'
    method = "hmy_getEpoch"
    params = []
    epoch = get_information(url, method, params)['result']
    return int(epoch, 16)

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
    
    endpoint = ['https://api.s0.os.hmny.io/', 'https://api.s1.os.hmny.io/', 'https://api.s2.os.hmny.io/', 'https://api.s3.os.hmny.io/']
    
    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'csv'))
    data = path.join(data, 'pure_delegator')
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make csv directory")
            exit(1)
            
    print("-- Data Processing --")
    validator_infos = getAllValidatorInformation()
    del_reward = defaultdict(int)
    del_stake = defaultdict(int)
    undel = defaultdict(int)
    val_address = []
    epoch = getEpoch()
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
            for u in d['undelegations']:
                if epoch - u['epoch'] <= 7:
                    undel[del_address] += u['amount']/1e18
                
    del_address = set(del_reward.keys()) - set(val_address)
    balance = dict()
    normal_transaction = defaultdict(int)
    for i in del_address:
        balance[i] = float(getBalance(i)/1e18)
        for shard in range(len(endpoint)):
            normal_transaction[i] += getTransactionCount(shard, i)
    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance (ONEs available = initial balance - current delegation - fees - pending undelgation  + claim rewards)'])
    normal_transaction_df = pd.DataFrame(normal_transaction.items(), columns = ['address', 'normal-transaction-count'])

    new_del_reward = dict()
    new_del_stake = dict()
    new_undel = dict()
    for k,v in del_reward.items():
        if k in del_address:
            new_del_reward[k] = v
            new_del_stake[k] = del_stake[k]
            new_undel[k] = undel[k]
    reward_df = pd.DataFrame(new_del_reward.items(), columns=['address', 'lifetime-reward (total rewards - claim rewards)'])
    stake_df = pd.DataFrame(new_del_stake.items(), columns=['address', 'stake (total delegated stake)'])
    undel_df = pd.DataFrame(new_undel.items(), columns=['address', 'pending undelegation'])
    df = reward_df.join(stake_df.set_index('address'), on = 'address')
    df = df.join(balance_df.set_index('address'), on = 'address')
    df = df.join(normal_transaction_df.set_index('address'), on = 'address')
    df = df.join(undel_df.set_index('address'), on = 'address')
    time = datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S") 
    print("-- Save csv files to ./csv/pure_delegator/{:s}_delegator.csv --".format(time))
    df.to_csv(path.join(data, '{:s}_delegator.csv'.format(time)))
    
    print("-- Filter the delegators in the google sheet --")
    html = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDAqXO-xVP4UwJlNJ6Qaws4N-TZ3FNZXqiSidPzU1I8pX5DS063d8h0jw84QhPmMDVBgKhopHhilFy/pub?gid=0&single=true&output=csv'
    delegator = read_csv(html)
    df['filter'] = df.apply(lambda c: True if c['address'] in delegator else False, axis = 1)
    filter_df = df[df['filter']].reset_index(drop = True)
    filter_df.to_csv(path.join(data, '{:s}_filter_delegator.csv'.format(time)))
    print("-- Save csv files to ./csv/pure_delegator/{:s}_delegator.csv --".format(time))

