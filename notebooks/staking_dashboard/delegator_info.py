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
    dels = defaultdict(int)
    val_address = []
    name = dict()
    website = dict()
    # get the accumualted reward in current block
    for info in validator_infos:
        address = info['validator']['address']
        val_address.append(address)
        name[address] = info['validator']['name']
        website[address] = info['validator']['website']
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            dels[del_address] += reward

    del_address = set(dels.keys()) - set(val_address)
    balance = dict()
    for i in del_address:
        balance[i] = getBalance(i)/1e18
    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance'])
    
    new_dels = dict()
    for k,v in dels.items():
        if k in del_address:
            new_dels[k] = v
    reward = pd.DataFrame(new_dels.items(), columns=['address', 'lifetime-reward'])
    df = reward.join(balance_df.set_index('address'), on = 'address')
    print("-- Save csv files to ./csv/ folder --")
    df.to_csv(path.join(data, 'delegator.csv'))

