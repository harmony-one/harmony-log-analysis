#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
import os
from os import path
import requests
import csv
import re
from collections import defaultdict
import argparse

base = path.dirname(path.realpath(__file__))
data = path.abspath(path.join(base, 'csv'))

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

def getBlockNumber():
    method = "hmy_blockNumber"
    params = []
    num = get_information(method, params)['result']
    return int(num, 16)

def get_size(size):
    html_url = "https://staking-explorer2-268108.appspot.com/networks/harmony-open-staking/validators_with_page?active=true&page=0&search=&size={}&sortOrder=desc&sortProperty=expectedReturns".format(size)
    res = requests.get(html_url)
    content = json.loads(res.content)
    return content['total']

def get_validator(page, size):
    html_url = "https://staking-explorer2-268108.appspot.com/networks/harmony-open-staking/validators_with_page?active=false&page={}&search=&size={}&sortOrder=desc&sortProperty=expectedReturns".format(page, size)
    res = requests.get(html_url)
    content = json.loads(res.content)
    return content['validators']

def read_csv(csv_file) -> (dict, list):
    r = requests.get(csv_file)
    s = [x.decode(encoding) for x in r.content.splitlines()]
    d = defaultdict(list)
    v = []
    dup_list = []
    for line in csv.reader(s):
        group = line[1].strip()
        email = line[3].strip()
        address = line[7].strip()
        if group in groups and re.match('one1', address) != None:
            d[group].append(address)
            v.append(address)
    return d, v

def diffAndFilter(map1, map2):
    map3 = dict()
    for k, v in map2.items():
        if k in map1:
            if v - map1[k] != 0:
                map3[k] = v - map1[k]
    return map3

def getNewValidatorInfo(address, df):
    index = df[df['address'] == address].index[0]
    return df.loc[index]['name'], df.loc[index]['security-contact'], df.loc[index]['website']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--new_validators', action = 'store_true', help = 'Print the new validators who are not in harmony.one/keys')
    parser.add_argument('--epos_status', action = 'store_true', help = 'Print the statistic of epos-status for all validators on staking dashboard')
    parser.add_argument('--all', action = 'store_true', help = 'Print all information')
    parser.add_argument('--output_file', default = 'validator_info', help = 'File name for the csv')
    
    bls_key, availability, name, epos_status, apr, delegation, committee, website, details, address, security, identity = [], [], [], [], [], [], [], [], [], [], [], []
    dels = defaultdict(int)
    
    args = parser.parse_args()
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make csv directory")
            exit(1)
            
    print("-- Data Processing --")
    # get the accumualted reward in current block
    block = getBlockNumber()
    next_block = block + 1
    validator_infos = getAllValidatorInformation()
    for info in validator_infos:  
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            dels[del_address] += reward
            
    # get the new accumulated reward in next block
    print("-- Need to wait for the next block to get the reward changes --")
    while block < next_block:
        block = getBlockNumber()
        
    validator_infos = getAllValidatorInformation()
    new_dels = defaultdict(int)
    for info in validator_infos:
        if not info['metrics']:
            bls_key.append(np.nan)
        else:
            bls_key.append(len(info['metrics']['by-bls-key']))
        if not info['current-epoch-performance']:
            availability.append(np.nan)
        else:
            availability.append(info['current-epoch-performance']['current-epoch-signing-percent'])
        name.append(info['validator']['name'])
        epos_status.append(info['epos-status'])
        apr.append(info['lifetime']['apr'])
        delegation.append(len(info['validator']['delegations'][0]))
        committee.append(info['currently-in-committee'])
        website.append(info['validator']['website'])
        details.append(info['validator']['details'])
        address.append(info['validator']['address'])
        security.append(info['validator']['security-contact'])
        identity.append(info['validator']['identity'])    
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            new_dels[del_address] += reward
    # get the reward the validator earned in that block
    reward_dict = diffAndFilter(dels, new_dels)
    
    # get most infos except reward and uptime
    df = pd.DataFrame(list(zip( name, address, website, details, security, identity, epos_status, committee, apr, delegation, bls_key,  availability)), columns =['name','address', 'website','details','security-contact','identity','epos-status', 'currently-in-committee', 'apr', 'delegator-num', 'bls-key-num', 'availability'])
    df = pd.concat([df.drop(['availability'], axis=1), df['availability'].apply(pd.Series)], axis=1)
    df.drop([0], axis = 1, inplace = True)
    df.reset_index(inplace = True, drop = True)
    
    # get reward per block
    reward = pd.DataFrame(reward_dict.items(), columns=['address', 'reward'])
    df = df.join(reward.set_index("address"), on = 'address')
    
    # get accumulated reward
    acc_reward = pd.DataFrame(new_dels.items(), columns=['address', 'acc_reward'])
    df = df.join(acc_reward.set_index("address"), on = 'address')
    # get uptime
    
    size = get_size(1)
    pages = size // 100 + 1
    
    # get the uptime
    validator = []
    for i in range(pages):
        val = get_validator(i,100)
        validator.extend(val)
    uptime = []
    address = []
    for i in validator:
        uptime.append(i['uptime_percentage'])
        address.append(i['address'])
    uptime_df = pd.DataFrame(list(zip(uptime, address)), columns = ['uptime-percentage','address'])
    df = df.join(uptime_df.set_index("address"), on = 'address')
    
    print("-- Save csv files to ./csv/ folder --")
    df.to_csv(path.join(data, args.output_file) + ".csv", index = False)
    
    if args.epos_status or args.all:
        print("-- Epos Status Summary --")
        count = df.groupby('epos-status')['epos-status'].count().reset_index(name = 'count')
        elected, eligible, ineligible = count['count'][0], count['count'][1], count['count'][2]
        print("Currently elected: %s \nEligible to be elected next epoch: %s \nNot eligible to be elected next epoch: %s \n" % (elected, eligible, ineligible))
    
    if args.new_validators or args.all:
        print("-- Processing csv file on harmony.one/keys --")
        csv_link = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUUOCAuSgP8TcA1xWY5AbxaMO7OSowYgdvaHpeMQudAZkHkJrf2sGE6TZ0hIbcy20qpZHmlC8HhCw1/pub?gid=0&single=true&output=csv'
        encoding = 'utf-8'
        groups = ['team', 'p-ops', 'foundational nodes', 'p-volunteer', 'hackers', 'community', 'partners']
        by_group, csv_validators = read_csv(csv_link)
        new_validators = [x for x in df['address'] if x not in csv_validators]

        print("-- New Validators --")
        print("New Validators: %d" % len(new_validators))
        for i in new_validators:
            name, security, website = getNewValidatorInfo(i, df)
            print("Address: %s, Validator Name: %s, Security Contact: %s, Website: %s" %(i, name, security, website))

