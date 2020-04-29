#!/usr/bin/env python
# coding: utf-8
import json
import requests
from collections import defaultdict

def get_information(method, params):
    url = 'https://api.s0.os.hmny.io/'
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    content = json.loads(r.content)
    return content

def getCommittees():
    method = "hmy_getSuperCommittees"
    params = []
    return get_information(method, params)['result']['current']

def getAllValidator():
    method = 'hmy_getAllValidatorAddresses'
    params = []
    return get_information(method, params)['result'] 

def getAllValidatorInformation():
    method = 'hmy_getAllValidatorInformation'
    params = [-1]
    return get_information(method, params)['result']

def getAllElectedValidator():
    method = "hmy_getElectedValidatorAddresses"
    params =[]
    return get_information(method, params)['result']

def getValidatorInfo(validator):
    method = "hmy_getValidatorInformation"
    params = [validator]
    return get_information(method, params)

def getEligibleValidator():
    eligible = []
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['epos-status'] == 'currently elected' or i['epos-status'] == 'eligible to be elected next epoch':
            address = i['validator']['address']
            eligible.append(address)
    return eligible

def getBlockNumber():
    method = "hmy_blockNumber"
    params = []
    num = get_information(method, params)['result']
    return int(num, 16)

def getLastBlockOfCurrentEpoch():
    method = 'hmy_getStakingNetworkInfo'
    params = []
    return get_information(method, params)['result']['epoch-last-block']

def getCurrentAndLastBlock():
    block = getBlockNumber()
    last_block = getLastBlockOfCurrentEpoch()
    return block, last_block

def getEpoch():
    method = "hmy_getEpoch"
    params = []
    epoch = get_information(method, params)['result']
    return int(epoch, 16)

def getEposMedian():
    method = "hmy_getMedianRawStakeSnapshot"
    params = []
    return float(get_information(method, params)['result']['epos-median-stake'])

def getMedianRawStakeSnapshot():
    method = "hmy_getMedianRawStakeSnapshot"
    params = []
    return get_information(method, params)['result']

def get_median(lst):
    n = len(lst) 
    lst.sort() 
    if n % 2 == 0: 
        median1 = lst[n//2] 
        median2 = lst[n//2 - 1] 
        median = (median1 + median2)/2
    else: 
        median = lst[n//2] 
    return median

def getRewards():
    rewards = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['currently-in-committee'] == True:
            address = i['validator']['address']
            reward_accumulated = i['lifetime']['reward-accumulated']
            rewards[address] = reward_accumulated
    return rewards

def getStakeRewardsDelegateAndShards():
    stakes = dict()
    rewards = dict()
    shards = dict()
    delegations = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['metrics']:
            address = i['validator']['address']
            reward_accumulated = i['lifetime']['reward-accumulated']
            rewards[address] = reward_accumulated
            delegations[address] = i['total-delegation']
            by_shard_metrics = i['metrics']['by-bls-key']
            v_stakes = dict()
            v_shards = dict()
            for by_shard_metric in by_shard_metrics:
                bls_key = by_shard_metric['key']['bls-public-key']
                e_stake = float(by_shard_metric['key']['effective-stake'])
                shard_id = by_shard_metric['key']['shard-id']
                v_stakes[bls_key] = e_stake
                v_shards[bls_key] = shard_id
            stakes[address] = v_stakes
            shards[address] = v_shards            
    return rewards, stakes, delegations, shards

def getStakedAmount():
    method = 'hmy_getStakingNetworkInfo'
    params = []
    num = get_information(method, params)['result']['total-staking']
    return int(num)

def getStakingMetrics():
    method = "hmy_getStakingNetworkInfo"
    params = []
    result = get_information(method, params)['result']
    supply = float(result['circulating-supply'])
    stake = float(result['total-staking']) / 1e18
    return supply, stake

def getStakesAndAprs():
    stakes = dict()
    aprs = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['metrics']:
            address = i['validator']['address']
            effective_stake = 0
            for j in i['metrics']['by-bls-key']:
                effective_stake += float(j['key']['effective-stake'])
            apr = float(i['lifetime']['apr'])
            stakes[address] = effective_stake
            aprs[address] = apr
    return stakes, aprs

def getAprByShards():
    count = defaultdict(int)
    apr_sum = defaultdict(int)
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['currently-in-committee'] == True:
            apr = float(i['lifetime']['apr'])
            for s in i['metrics']['by-bls-key']:
                shard = s['key']['shard-id']
                count[shard] += 1
                apr_sum[shard] += apr
    apr_avg = dict()
    for k,v in apr_sum.items():
        apr_avg[k] = v/count[k]
    return apr_avg

def getAvailabilityAndRewards():
    reward = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['current-epoch-performance']: # check whether he is eligible
            sign = i['current-epoch-performance']['current-epoch-signing-percent']
            if sign['current-epoch-to-sign'] == 0:
                continue
            perc = sign['current-epoch-signed']/sign['current-epoch-to-sign']
            if perc > 2/3:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                reward[address] = reward_accumulated
    return reward

def getRewardsAndStatus(cutoff):
    reward = dict()
    status = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        address = i['validator']['address']
        if address in cutoff: 
            reward_accumulated = i['lifetime']['reward-accumulated']
            reward[address] = reward_accumulated
            epos_status = i['epos-status']
            status[address] = epos_status
    return reward, status

def getStakeAndUndelegate(epoch):
    validator = dict()
    undelegate = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        address = i['validator']['address']
        validator[address] = i['total-delegation']
        undel = 0
        for d in i['validator']['delegations']:
            for j in d['undelegations']:
                if epoch == j['epoch']:
                    undel += j['amount']
        undelegate[address] = undel
    return validator, undelegate

def getStakeAndUndelegate2(epoch):
    validator = dict()
    undelegate = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        address = i['validator']['address']
        stake = dict()
        undel = dict()
        for d in i['validator']['delegations']:
            del_address = d['delegator-address']
            del_amount = d['amount']
            if not d['undelegations']:
                undel_amount = 0
            flag = False
            for j in d['undelegations']:
                if epoch == j['epoch']:
                    flag = True
                    undel_amount = j['amount']
                    break
            if not flag:
                undel_amount = 0
            undel_num = d['undelegations']
            stake[del_address] = del_amount
            undel[del_address] = undel_amount
        validator[address] = stake
        undelegate[address] = undel
    return validator, undelegate

def diffAndFilter(map1, map2):
    map3 = dict()
    for k, v in map2.items():
        if k in map1:
            if v - map1[k] != 0:
                map3[k] = v - map1[k]
    return map3

def diffAndFilter2(map1, map2):
    map3 = dict()
    for key, val in map2.items():
        diff = dict()
        for k, v in map2[key].items():
            if v - map1[key][k] != 0:
                diff[k] = v - map1[key][k]
        map3[key] = diff
    return map3

def getAdjustment():
    method = 'hmy_getCurrentUtilityMetrics'
    params = []
    num = get_information(method, params)['result']['Adjustment']
    return float(num)

def getBlockSigners(blockNum):
    method = 'hmy_getBlockSigners'
    params = [blockNum]
    return get_information(method, params)['result']

def proportional(l1, l2):
    return l1 == l2

def extract(lst): 
    return [item[0] for item in lst] 

def check(lst1, lst2):
    keys1 = [item[0] for item in lst1]
    keys2 = [item[0] for item in lst2]
    stakes = [item[1] for item in lst1]
    rewards = [item[1] for item in lst2]
    l = len(keys1)
    i = 0
    j = 0
    while i < l:
        if keys1[i] == keys1[i]:
            i = i + 1
        else:
            stake = stakes[i]
            reward = rewards[i]
            i1 = i
            i2 = i
            j = i
            while stakes[i1] == stake:
                i1 = i1 + 1
            while rewards[i2] == reward:
                i2 = i2 + 1
            if i1 != i2:
                return False
            while i < i1:
                k = j
                found = False
                while k < i2:
                    if keys1[i] == keys2[k]:
                        found = True
                        break
                    k = k + 1
                if found == False:
                    return False
                i = i + 1
            i = i1
    return True   


    

