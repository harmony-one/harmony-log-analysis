#!/usr/bin/env python
# coding: utf-8
import json
import pandas as pd
import os
from os import path
import requests
from collections import defaultdict

def get_information(method, params):
    url = 'https://api.s0.os.hmny.io/'
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    content = json.loads(r.content)
    return content

def getAllValidatorInformation():
    method = 'hmy_getAllValidatorInformation'
    params = [-1]
    return get_information(method, params)['result']

def getBalance(address):
    method = "hmy_getBalance"
    params = [address, "latest"]
    return int(get_information(method, params)['result'],16)

def getTransactionCount(address):
    method = "hmy_getTransactionCount"
    params = [address, 'latest']
    return int(get_information(method, params)['result'],16)

def getEpoch():
    method = "hmy_getEpoch"
    params = []
    epoch = get_information(method, params)['result']
    return int(epoch, 16)

if __name__ == "__main__":
    
    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'csv'))
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
    transaction = dict()
    for i in del_address:
        balance[i] = float(getBalance(i)/1e18)
        transaction[i] = getTransactionCount(i)
    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance (ONEs available = initial balance - current delegation - pending undelgation  + claim rewards)'])
    transaction_df = pd.DataFrame(transaction.items(), columns = ['address', 'transaction-count'])
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
    df = df.join(transaction_df.set_index('address'), on = 'address')
    df = df.join(undel_df.set_index('address'), on = 'address')
    print("-- Save csv files to ./csv/ folder --")
    df.to_csv(path.join(data, 'delegator.csv'))

