#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
import os
from os import path
import time
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

def read_csv(csv_file) -> (dict, list, list):
    r = requests.get(csv_file)
    s = [x.decode(encoding) for x in r.content.splitlines()]
    d = defaultdict(list)
    v = []
    id_name = []
    for line in csv.reader(s):
        group = line[1].strip()
        id_num = re.sub(r'/\d+$', '', line[3].strip())
        address = line[7].strip()
        if group in groups and re.match('one1', address) != None:
            d[group].append(address)
            v.append(address)
            id_name.append(id_num)
    return d, v, id_name

def drop_duplicate(df):
    dp = df[(df['id_name'] != "") & (df.id_name.notnull())]
    dp = dp[dp.id_name.str.contains("www.ankr.com") == False]
    df = df.loc[list(set(df.index) - set(dp[dp.duplicated(subset = ['id_name'])].index))]
    return df

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
    parser.add_argument('--epos_status_unique', action = 'store_true', help = 'Print the statistic of epos-status for all unique validators on staking dashboard')
    parser.add_argument('--all', action = 'store_true', help = 'Print all information')
    parser.add_argument('--output_file', default = 'validator_info', help = 'File name for the csv')
    
    bls_key, availability, name, epos_status, apr, delegation, committee, website, details, address, security, identity, boot_status = [], [], [], [], [], [], [], [], [], [], [], [], []
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
        boot_status.append(info['booted-status'])
        for d in info['validator']['delegations']:
            del_address = d['delegator-address']
            reward = d['reward']/1e18
            new_dels[del_address] += reward
    print("-- Calculate the reward --")
    # get the reward the validator earned in that block
    reward_dict = diffAndFilter(dels, new_dels)

    # get most infos except reward and uptime
    df = pd.DataFrame(list(zip( name, address, website, details, security, identity, epos_status, committee, apr, delegation, bls_key, boot_status)), columns =['name','address', 'website','details','security-contact','identity','epos-status', 'currently-in-committee', 'apr', 'delegator-num', 'bls-key-num', 'boot_status'])
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
    # get the validator info
    validator = []
    for i in range(pages):
        val = get_validator(i,100)
        validator.extend(val)
    uptime = []
    address = []
    active_nodes = []
    elected_nodes = []
    active = []
    for i in validator:
        uptime.append(i['uptime_percentage'])
        address.append(i['address'])
    uptime_df = pd.DataFrame(list(zip(uptime, address)), columns = ['uptime-percentage','address'])
    df = df.join(uptime_df.set_index("address"), on = 'address')
    df.to_csv(path.join(data, args.output_file) + ".csv", index = False)

    if args.epos_status or args.all:
        print("-- Epos Status Summary --")
        count = df.groupby('epos-status')['epos-status'].count().reset_index(name = 'count')
        elected, eligible, ineligible = count['count'][0], count['count'][1], count['count'][2]
        print("Currently elected: %s \nEligible to be elected next epoch: %s \nNot eligible to be elected next epoch: %s \n" % (elected, eligible, ineligible))
    
    if args.epos_status_unique or args.new_validators or args.all:
        print("-- Processing csv file on harmony.one/keys --")        
        csv_link = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTUUOCAuSgP8TcA1xWY5AbxaMO7OSowYgdvaHpeMQudAZkHkJrf2sGE6TZ0hIbcy20qpZHmlC8HhCw1/pub?gid=0&single=true&output=csv'
        encoding = 'utf-8'
        groups = ['team', 'p-ops', 'foundational nodes', 'p-volunteer', 'hackers', 'community', 'partners']
        by_group, csv_validators, id_name = read_csv(csv_link)

    if args.epos_status_unique or args.all:
        print("-- Epos Status Summary (Unique) --")
        id_df = pd.DataFrame(list(zip(csv_validators, id_name)), columns = ['address','id_name'])
        id_df.drop_duplicates(subset = ['address'], inplace = True)
        new_df = df.join(id_df.set_index('address'), on = 'address')
        lst = []
        for name, group in new_df.groupby('epos-status'):
            lst.append(drop_duplicate(group))
        new = pd.concat(lst)
        new_count = new.groupby('epos-status')['epos-status'].count().reset_index(name = 'count')
        elected, eligible, ineligible = new_count['count'][0], new_count['count'][1], new_count['count'][2]
        print("Currently elected: %s \nEligible to be elected next epoch: %s \nNot eligible to be elected next epoch: %s \n" % (elected, eligible, ineligible))

        print("-- Duplicate Validators --")
        dp = new_df[(new_df['id_name'] != "") & (new_df.id_name.notnull())]
        dp = dp[dp.id_name.str.contains("www.ankr.com") == False]
        dp_count = dp.groupby('id_name')['id_name'].count().reset_index(name = 'count')
        lst = dp_count[dp_count['count'] > 1].id_name.tolist()
        dp['is_duplicated'] = dp['id_name'].apply(lambda x: True if any(i in x for i in lst) else False)
        dp_address = dp[(dp['is_duplicated'])][['address', 'name', 'id_name', 'epos-status']].sort_values(by = 'id_name').reset_index(drop = True)
        dp_address.to_csv(path.join(data,'duplicate_validators.csv'), index = False)
        print("Save duplicate validators to ./csv/duplicate_validators.csv")

    if args.new_validators or args.all:
        new_validators = [x for x in df['address'] if x not in csv_validators]
        print("-- New Validators --")
        print("New Validators: %d" % len(new_validators))
        for i in new_validators:
            name, security, website = getNewValidatorInfo(i, df)
            print("Address: %s, Validator Name: %s, Security Contact: %s, Website: %s" %(i, name, security, website))

