#!/usr/bin/env python
# coding: utf-8
import json
import pandas as pd
import numpy as np
import os
import time
import requests
from collections import defaultdict
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("economic-test")
logger.setLevel(logging.INFO)
filename = "./logs/report_log_{}.log".format(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S_%f'))
file_handler = logging.FileHandler(filename)
formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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
    logger.info(f"current and last block numbers: {block}, {last_block}")
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

def getStakeRewardsAndShards():
    stakes = dict()
    rewards = dict()
    shards = dict()
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        if i['metrics']:
            address = i['validator']['address']
            reward_accumulated = i['lifetime']['reward-accumulated']
            rewards[address] = reward_accumulated
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
    return rewards, stakes, shards

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
        if i['current-epoch-performance']:
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

def E1_test():
    global curr_test
    logger.info(f"Test-E1: A staked validator whose stake is in the top #slots stakes is always considered for election")
    try:
        committees = getCommittees()
        slot = committees['external-slot-count']
        block, last_block = getCurrentAndLastBlock()
        if block == last_block:
            logger.info(f"current block is the last block in epoch, waiting for the new epoch...")
            new_block = block+1
            while block < new_block:
                block = getBlockNumber()
            block, last_block = getCurrentAndLastBlock()
        second_last_block = last_block - 1
        while block < second_last_block:
            block = getBlockNumber()
        logger.info(f"second last block in current epoch reached, {block}, wait for 6 seconds to reach the end of the block")
        time.sleep(6)
        logger.info("begin collecting eligible validators...")
        # get top #slots nodes who are eligible to elected next epoch
        validator_infos = getAllValidatorInformation()
        eligible = []
        stake = dict()
        for i in validator_infos:
            if i['epos-status'] == 'currently elected' or i['epos-status'] == 'eligible to be elected next epoch':
                address = i['validator']['address']
                eligible.append(address)
                stake[address] = i['total-delegation']

        if len(eligible) > slot:
            sorted_stake = sorted(stake.items(), key=lambda kv: kv[1], reverse = True)
            eligible = [kv[0] for kv in sorted_stake[:slot]]

        # wait for epoch changes
        new_block = block + 2
        while block < new_block:
            block = getBlockNumber()
        logger.info(f"first block in new epoch reached, {block}, will wait for 5 seconds to begin testing...")
        time.sleep(5)
        # check whether the eligible validators are selected
        validator_infos = getAllValidatorInformation()
        flag = True
        for i in validator_infos:
            if i in eligible:  
                if i['epos-status'] != 'currently elected':
                    logger.warning(f"Test E1: Fail")
                    logger.warning(f"validator {i['validator']['address']} who is eligible to be elected is not elected")
                    flag = False
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = E2_test
    if flag:
        logger.info(f"Test E1: Succeed")
        return True
    else:
        return False

def E2_test():
    global curr_test
    logger.info(f"Test-E2: Joining after the election start must not consider the validator ")
    curr_test = E3_test
    flag = True
    num = 1
    iterations = 0
    new_count = 0
    try:
        while iterations < num:
            # get the last block in current epoch
            block, last_block = getCurrentAndLastBlock()
            while block < last_block - 1:
                block = getBlockNumber()
            logger.info(f"last second block in the current epoch reached {block} will begin collecting existing eligible validators after 5 seconds")
            time.sleep(5)
            eligible_old = getEligibleValidator()

            while block < last_block:
                block = getBlockNumber()
            logger.info(f"last block in the current epoch reached {block} will begin collecting new eligible validators after 5 seconds")
            time.sleep(5)
            eligible_current = getEligibleValidator()

            logger.info(f"checking whether we have validators who set their status active after election starts")
            eligible_new = set(eligible_current) - set(eligible_old)
            if not eligible_new:
                logger.info(f"no validator joins after the election start in this test")
            else:
                new_count += 1
                while block < last_block + 1:
                    block = getBlockNumber()
                logger.info(f"first block in the current epoch reached {block} will wait for 5 seconds to begin collecting elected infos")
                time.sleep(3)
                logger.info(f"begin checking validators who joined after the election was elected...")
                validators = getAllValidatorInformation()
                for i in validators:
                    if i['validator']['address'] in eligible_new:
                        if i['currently-in-committee']:
                            logger.warning(f"Test-E2: Fail")
                            logger.warning(f"Validator  {i} joining after the election was considered for election")
                            flag = False
            iterations += 1
    except TypeError as e:
        logger.error(f"error: {e}")
    if new_count == 0:
        logger.info(f"No validator joined after the election, need more tests")
        return "Need More Tests"
    if flag:
        logger.info(f"Test-E2: Succeed")
        return True
    else:
        return False

def E3_test():
    global curr_test
    logger.info(f"Test-E3: Joining before election start must consider the validator for election")
    try:
        committees = getCommittees()
        slot = committees['external-slot-count']
        iterations = 0
        num = 1
        while iterations < num:
            block, last_block = getCurrentAndLastBlock()
            if block == last_block:
                logger.info(f"current block is the last block in epoch, waiting for the new epoch...")
                new_block = block+1
                while block < new_block:
                    block = getBlockNumber()
                block, last_block = getCurrentAndLastBlock()
            second_last_block = last_block - 1
            while block < second_last_block:
                block = getBlockNumber()
            logger.info(f"second last block in current epoch reached, {block}, wait for 6 seconds to reach the end of the block")
            time.sleep(6)
            logger.info("begin collecting eligible validators...")
            # get top #slots nodes who are eligible to elected next epoch
            validator_infos = getAllValidatorInformation()
            eligible = []
            stake = dict()
            for i in validator_infos:
                if i['epos-status'] == 'currently elected' or i['epos-status'] == 'eligible to be elected next epoch':
                    address = i['validator']['address']
                    eligible.append(address)
                    stake[address] = i['total-delegation']

            if len(eligible) > slot:
                sorted_stake = sorted(stake.items(), key=lambda kv: kv[1], reverse = True)
                eligible = [kv[0] for kv in sorted_stake[:slot]]

            # wait for epoch changes
            new_block = block + 2
            while block < new_block:
                block = getBlockNumber()
            logger.info(f"first block in new epoch reached, {block}, will wait for 5 seconds to begin testing...")
            time.sleep(5)
            # check whether the eligible validators are selected
            validator_infos = getAllValidatorInformation()
            flag = True
            for i in validator_infos:
                if i in eligible:  
                    if i['epos-status'] != 'currently elected':
                        logger.warning(f"Test-E3: Fail")
                        logger.warning(f"Validator {i} joined before election was not considered as the validator for election")
                        flag = False
            iterations += 1
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = E4_test
    if flag:
        logger.info(f"Test E3: Succeed")
        return True
    else:
        return False

def E4_test():
    global curr_test
    logger.info(f"Test-E4: Low staker will never get elected over high staker")
    # the number of epoches you want to test
    num = 1
    iterations = 0
    flag = True
    try:
        while iterations < num:
            block, last_block = getCurrentAndLastBlock()
            if block == last_block:
                logger.info(f"current block is the last block in epoch, waiting for the new epoch...")
                new_block = block+1
                while block < new_block:
                    block = getBlockNumber()
                block, last_block = getCurrentAndLastBlock()
            second_last_block = last_block - 1
            while block < second_last_block:
                block = getBlockNumber()
            logger.info(f"second last block in current epoch reached, {block}, wait for 6 seconds to reach the end of the block")
            time.sleep(6)
            logger.info(f"begin collecting eligible validators...")
            validator_infos = getAllValidatorInformation()
            eligible_stake = dict()
            for i in validator_infos:
                if i['epos-status'] == 'currently elected' or i['epos-status'] == 'eligible to be elected next epoch':
                    address = i['validator']['address']
                    eligible_stake[address] = i['total-delegation']
            # reach the first block in next epoch and check the status of all eligible validators
            new_epoch_block = block + 1
            while block < new_epoch_block:
                block = getBlockNumber()
            logger.info(f"first block of new epoch reached, {new_epoch_block}, will begin checking all the elgible validators' election result...")
            elected = dict()
            non_elected = dict()
            validator_infos = getAllValidatorInformation()
            for i in validator_infos:
                address = i['validator']['address']
                if address in eligible_stake:
                    if i['currently-in-committee']:
                        elected[address] = float(eligible_stake[address])
                    else:
                        non_elected[address] = float(eligible_stake[address])
            sorted_elected = sorted(elected.items(), key = lambda kv: kv[1])
            sorted_non_elected = sorted(non_elected.items(), key = lambda kv: kv[1], reverse = True)

            # get the lowest elected validator and highest non-elected validator
            if not sorted_elected:
                lowest_elected = 0
            else:
                lowest_elected = sorted_elected[0][1]
            if not sorted_non_elected:
                highest_unelected = 0
            else:
                highest_unelected = sorted_non_elected[0][1]
            if lowest_elected < highest_unelected:
                logger.warning(f"Test-E4: Fail")
                logger.warning(f"lowest stake in elected eligible validators: {sorted_elected[0]}" )
                logger.warning(f"highest stake in unelected eligible validators: {sorted_non_elected[0]}")
                flag = False
            iterations += 1
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = M2_test
    if flag:
        logger.info(f"Test-E4: Succeed")
        return True
    else:
        return False

def M2_test():
    global curr_test
    logger.info(f"Test-M2: Median is correctly computed for even and odd number of available slots")
    num = 1
    iterations = 0
    flag = True
    block, last_block = getCurrentAndLastBlock()
    if block == last_block:
        logger.info(f"currently at the last block, wait for new epoch starts...")
        while block < last_block+1:
            block = getBlockNumber()
    while iterations < num:
        epoch = getEpoch()
        logger.info(f"current epoch: {int(epoch, 16)}, begin testing...")
        # get the median from rpc call
        median = getEposMedian()
        # calculate the median manually
        slot_winners = getMedianRawStakeSnapshot()['epos-slot-winners']
        stake = []
        for i in slot_winners:
            stake.append((float(i['eposed-stake'])))
        cal_median = float(get_median(stake))
        # compare the calculated median and rpc median
        if cal_median != median:
            logger.warning(f"Test-M2: Fail")
            logger.warning(f"calculated median: {cal_median}")
            logger.warning(f"rpc median: {median}")
            flag = False
        iterations += 1  
        new_epoch = epoch + 1
        if num == 1:
            break
        logger.info(f"wait for new epoch starts...")
        while epoch < new_epoch:
            epoch = getEpoch()
        logger.info(f"wait for 3 seconds to begin testing...")    
        time.sleep(3)
    curr_test = M3_test
    if flag:
        logger.info(f"Test-M2: Succeed")
        return True
    else:
        return False
    
def M3_test():
    global curr_test
    logger.info(f"Test-M3: Median function stability: run median computation for x number of epoch to verify stability")
    num = 2
    iterations = 0
    flag = True
    while iterations < num:
        logger.info(f"test {iterations+1} will begin ...")
        block, last_block = getCurrentAndLastBlock()
        logger.info("wait until the new epoch begins ...")
        while block < last_block+1:
            block = getBlockNumber()
        logger.info("new epoch first block reached", block, "will wait for 5 secondss to begin testing...")
        time.sleep(5)
        # get the median from rpc call
        median = getEposMedian()
        # calculate the median manually
        slot_winners = getMedianRawStakeSnapshot()['epos-slot-winners']
        stake = []
        for i in slot_winners:
            stake.append((float(i['eposed-stake'])))
        cal_median = float(get_median(stake))
        # compare the calculated median and rpc median
        if cal_median != median:
            logger.warning(f"Test-M3: Fail")
            logger.warning(f"manually calculated median stake: {cal_median}")
            logger.warning(f"harmony apr call median stake: {median}")    
        iterations += 1  
    curr_test = M5_test
    if flag:
        logger.info(f"Test-M3: Succeed")
        return True
    else:
        return False

def M5_test():
    global curr_test
    logger.info(f"Test-M5: No effective stake is out of range: [median-0.15*median, median+0.15*median]")
    # get the median stake and the upper and lower level 
    result = getMedianRawStakeSnapshot()
    median = int(float(result['epos-median-stake']))
    lower = int(median- 0.15*median)
    upper = int(median + 0.15*median)
    logger.info("median stake is " + str(median))
    logger.info("lower bond is " + str(lower))
    logger.info("upper bond is " + str(upper))
    
    validator_infos = result['epos-slot-winners']
    count = 0
    flag = True
    for i in validator_infos:
        addr = i['slot-owner']
        stake = int(float(i['eposed-stake']))
        bls_key = i['bls-public-key']
        count += 1
        if stake > upper or stake < lower:
            logger.warning(f"Test-M5: Fail")
            logger.warning(f"validator: {addr} bls public key: {bls_key}") 
            logger.warning(f"effective stake is out of range. The effective stake is {stake}")
            flag = False
    logger.info(f"total slots verified: {count}" )
    curr_test = R1_test
    if flag:
        logger.info(f"Test-M5: Succeed")
        return True
    else:
        return False

def R1_test():
    global curr_test
    logger.info("Test R1: Harmony nodes should not earn block rewards")
    committees = getCommittees()
    harmony_nodes = []
    for k,v in committees['quorum-deciders'].items():
        for i in v['committee-members']:
            if i['is-harmony-slot'] == True:
                harmony_nodes.append(i['earning-account'])
    num = 0
    for i in harmony_nodes:
        if "error" in getValidatorInfo(i):
            num += 1
    curr_test = R2_test
    if num == len(harmony_nodes):
        logger.info("Test-R1: Succeed")
        return True
    else:
        logger.warning("Test-R1: Fail")
        return False

def R2_test():
    global curr_test
    logger.info(f"Test-R2: Not elected validators should not earn reward")
    block, last_block = getCurrentAndLastBlock()
    logger.info(f"wait until the new epoch begins at block number {last_block + 1}...")
    while block < last_block + 1:
        block = getBlockNumber()
    validator_infos = getAllValidatorInformation()
    not_elected = []
    rewards = dict()
    delegation_counts = dict()
    for i in validator_infos:
        if i['currently-in-committee'] == False:
            not_elected.append(i)
            address = i['validator']['address']
            amount = i['lifetime']['reward-accumulated']
            rewards[address] = amount
            delegation_counts[address] = len(delegations)

    block, last_block = getCurrentAndLastBlock()
    logger.info(f"wait until the end of the last block of this epoch {last_block + 1}...")
    while block < last_block:
        block = getBlockNumber()
    time.sleep(5)
    logger.info(f"begin testing...")
    # check the rewards
    failures = 0
    validator_infos = getAllValidatorInformation()
    for i in validator_infos:
        address = i['validator']['address']
        if address in not_eleccted:
            amount = i['lifetime']['reward-accumulated']
            if rewards[address] != amount:
                logger.warning(f"Error: reward not same for {address}, previous: {rewards[address]} new: {amount}")
                failures = failures + 1
    curr_test = R3_test
    if failures > 0:
        logger.warning(f"Test-R2: Fail")
        return False
    else:
        logger.info(f"Test-R2: Succeed")
        return True

def R3_test():
    global curr_test
    logger.info(f"Test-R3: High stakers earn more reward than low stakers")
    try:
        block, last_block = getCurrentAndLastBlock()
        new_epoch_block = last_block + 2 # first block is problematic, hence going for second.
        while block < new_epoch_block:
            block = getBlockNumber()
        logger.info(f"new epoch second block reached, {new_epoch_block}, will begin testing")
        rewards, stakes, shards = getStakeRewardsAndShards()
        logger.info(f"obtained second block stakes and rewards, total stakes found = {len(stakes)}, total rewards found = {len(rewards)}")
        new_epoch_block = block + 1
        while block < new_epoch_block:
            block = getBlockNumber()
        logger.info(f"new epoch third block reached, {block}, will begin comparing stakes and rewards")  
        flag = True
        new_rewards = getRewards()

        key_to_stake = dict()
        key_to_reward = dict()
        key_to_shard = dict()
        for addr, reward in new_rewards.items():
            if addr in rewards and addr in stakes and addr in shards:
                addr_reward = reward - rewards[addr]
                slots = len(stakes[addr])
                per_slot_reward = addr_reward / slots
                for key, stake in stakes[addr].items():
                    key_to_reward[key] = per_slot_reward
                    if key in stakes[addr]:
                        key_to_stake[key] = stakes[addr][key]
                    if key in shards[addr]:
                        key_to_shard[key] = shards[addr][key]

        shard_rewards = dict()
        shard_stakes = dict()
        for key, shard in key_to_shard.items():
            if shard not in shard_stakes:
                shard_stakes[shard] = dict()
            if shard not in shard_rewards:
                shard_rewards[shard] = dict()
            shard_stakes[shard][key] = key_to_stake[key]
            shard_rewards[shard][key] = key_to_reward[key]

        for shard in shard_rewards.keys():
            sorted_stakes = sorted(shard_stakes[shard].items(), key=lambda kv: kv[1], reverse = True)
            sorted_rewards = sorted(shard_rewards[shard].items(), key=lambda kv: kv[1], reverse = True)
            stake_keys = extract(sorted_stakes)
            reward_keys = extract(sorted_rewards)
            logger.info(f"comparison to begin, two lengths: {len(stake_keys)}, {len(reward_keys)}")
            if check(sorted_stakes, sorted_rewards) == False:
                logger.warning(f"on shard {shard}: Fail")
                logger.warning(f"validators sorted by stakes: {stake_keys}")
                logger.warning(f"validators sorted by reward: {reward_keys}")
                flag = False
            else:
                logger.info(f"on shard {shard}: Succeed")
                
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = R4_test
    if flag:
        logger.info(f"Test-R3: Succeed")
        return True
    else:
        logger.warning(f"Test-R3: Fail")
        return False

def R4_test():
    global curr_test
    logger.info(f"Test-R4: Reward given out to delegators sums up to the total delegation reward for each validator")
    try:
        block, last_block = getCurrentAndLastBlock()
        while last_block - block > 32:
            block = getBlockNumber()
        if block == last_block:
            logger.info(f"current at the last block, wait until the 6th block in the new epoch")
            while block < last_block+6:
                block = getBlockNumebr()
        logger.info(f"current block {block}, will begin collecting infos...")
        acc_rewards_prev = dict()
        delegations_prev = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_prev[address] = reward_accumulated
                ds = i['validator']['delegations']
                dels = dict()
                for d in ds:
                    d_addr = d['delegator-address']
                    d_reward = d['reward']
                    dels[d_addr] = d_reward
                delegations_prev[address] = dels  
        next_block = current_block + 1
        while current_block < next_block:
            current_block = getBlockNumber()
        logger.info(f"new block reached, {current_block}, will begin testing...")
        iterations = 0
        num = 1
        flag = True
        while iterations < num:
            logger.info(f"current block: {current_block}")
            # get the validator info and compute validator rewards
            acc_rewards_curr = dict()
            delegations_curr = dict()
            validator_infos = getAllValidatorInformation()
            for i in validator_infos:
                if i['currently-in-committee'] == True:
                    address = i['validator']['address']
                    reward_accumulated = i['lifetime']['reward-accumulated']
                    acc_rewards_curr[address] = reward_accumulated
                    if address not in acc_rewards_prev:
                        continue
                    reward = reward_accumulated - acc_rewards_prev[address]
                    if reward == 0:
                        continue
                    elif reward < 0:
                        reward = -reward # first time delegations
                    del_rewards = 0
                    dels = delegations_prev[address]
                    ds = i['validator']['delegations']
                    for d in ds:
                        d_addr = d['delegator-address']
                        d_reward = d['reward']
                        del_rewards += d['reward']
                        if d_addr in dels:
                            del_rewards -= dels[d_addr]
                    if del_rewards != reward:
                        logger.warning(f"Test-R4:Fail")
                        logger.warning(f"for validator {address}, validator reward: {reward:.20e}, delegators reward: {del_rewards:.20e}")
                        flag = False
                    delegations_curr[address] = ds

            last_block = current_block
            current_block = getBlockNumber()
            while current_block == last_block:
                current_block = getBlockNumber()

            acc_rewards_prev = acc_rewards_curr
            delegations_prev = delegations_curr
            iterations = iterations + 1            
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = R5_test
    if flag:
        logger.info(f"Test-R4: Succeed")
        return True
    else:
        return False

def R5_test():
    global curr_test
    logger.info(f"Test-R5: Reward given out to block signers sums up to the total block reward")
    try:
        block, last_block = getCurrentAndLastBlock()
        while last_block - block > 32:
            block = getBlockNumber()
        if block == last_block:
            logger.info(f"current at the last block, wait until the 6th block in the new epoch")
            while block < last_block+6:
                block = getBlockNumebr()
        logger.info(f"current block {block}, will begin collecting infos...")

        acc_rewards_prev = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_prev[address] = reward_accumulated
                
        next_block = block + 1
        while block < next_block:
            block = getBlockNumber()
        logger.info(f"new block {block} reached, will begin testing...")
        flag = True
        # get the validator info and compute validator rewards
        acc_rewards_curr = dict()
        validator_infos = getAllValidatorInformation()
        block_reward = 28e18
        validator_rewards = 0
        total_reward = 0
        signers = 0
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                signers += 1
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                key_metrics = i['metrics']['by-bls-key']
                validator_reward = 0
                for by_key in key_metrics:
                    validator_addr = by_key['key']['earning-account']
                    by_key_reward = block_reward * float(by_key['key']['overall-percent']) / 0.32
                    validator_reward += by_key_reward
                acc_rewards_curr[address] = reward_accumulated
                reward = reward_accumulated
                if address in acc_rewards_prev:
                    reward -= acc_rewards_prev[address]
                total_reward += reward
                validator_rewards += validator_reward
        if total_reward != validator_rewards:        
            logger.warning(f"Test-R5: Fail")
            logger.warning(f"block: {current_block}, validator block reward: {validator_rewards:.20e}, total reward: {total_reward:.20e}, signers: {signers}")
            flag = False

    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = R6_test
    if flag:
        logger.info(f"Test-R5: Succeed")
        return True
    else:
        return False

def R6_test():
    global curr_test
    logger.info(f"Test-R6: Tests whether the delegation reward is distributed correctly")
    try:
        block, last_block = getCurrentAndLastBlock()
        while last_block - block > 32:
            block = getBlockNumber()
        if block == last_block:
            logger.info(f"current at the last block, wait until the 6th block in the new epoch")
            while block < last_block+6:
                block = getBlockNumebr()
        logger.info(f"current block {block}, will begin collecting infos...")

        acc_rewards_prev = dict()
        delegations_prev = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_prev[address] = reward_accumulated
                ds = i['validator']['delegations']
                dels = dict()
                for d in ds:
                    d_addr = d['delegator-address']
                    d_reward = d['reward']
                    dels[d_addr] = d_reward
                delegations_prev[address] = dels

        next_block = block + 1
        while block < next_block:
            block = getBlockNumber()
        logger.info(f"new block {block} reached, will begin testing...")
        flag = True
        # get the validator info and compute validator rewards
        acc_rewards_curr = dict()
        delegations_curr = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                if address != "one1tpxl87y4g8ecsm6ceqay49qxyl5vs94jjyfvd9":
                    continue
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_curr[address] = reward_accumulated
                if address not in acc_rewards_prev:
                    continue
                reward = reward_accumulated - acc_rewards_prev[address]
                if reward == 0:
                    continue
                elif reward < 0:
                    reward = -reward # first time delegations
                commission = float(i['validator']['rate']) * reward
                total_delegation_reward = reward - commission
                total_delegation = i['total-delegation']
                ds = i['validator']['delegations']
                del_rewards = 0
                dels = delegations_prev[address]
                dels_curr = dict()
                for d in ds:
                    d_addr = d['delegator-address']
                    d_reward = d['reward']
                    dels_curr[d_addr] = d_reward
                    d_amount = d['amount']
                    delegation_reward_actual = d_reward
                    if d_addr in dels:
                        delegation_reward_actual = delegation_reward_actual - dels[d_addr]
                    percentage = d_amount / total_delegation
                    delegation_reward_expected = percentage * total_delegation_reward
                    if d_addr == address:
                        delegation_reward_expected = delegation_reward_expected + commission
                    if delegation_reward_actual != delegation_reward_expected:
                        logger.warning(f"Test-R6: Fail")
                        logger.warning(f"for validator {address} delegation {d_addr}, expected: {delegation_reward_expected:.20e}, actual: {delegation_reward_actual:.20e}")
                        flag = False
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = R7_test
    if flag:
        logger.info(f"Test-R6: Succeed")
        return True
    else:
        return False

def R7_test():
    global curr_test
    logger.info(f"Test-R7: Sum of validator and delegator earning should match the block reward")
    try:
        block, last_block = getCurrentAndLastBlock()
        while last_block - block > 32:
            block = getBlockNumber()
        if block == last_block:
            logger.info(f"current at the last block, wait until the 6th block in the new epoch")
            while block < last_block+6:
                block = getBlockNumebr()
        logger.info(f"current block {block}, will begin collecting infos...")
        
        acc_rewards_prev = dict()
        delegations_prev = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_prev[address] = reward_accumulated
                ds = i['validator']['delegations']
                dels = dict()
                for d in ds:
                    d_addr = d['delegator-address']
                    d_reward = d['reward']
                    dels[d_addr] = d_reward
                delegations_prev[address] = dels

        next_block = block+1
        while block < next_block:
            block = getBlockNumber()
        logger.info(f"new block {block} reached, will begin testing...")
        iterations = 0
        num = 1
        flag = True
        # get the validator info and compute validator rewards
        acc_rewards_curr = dict()
        delegations_curr = dict()
        validator_infos = getAllValidatorInformation()
        block_reward = 28e18
        validator_rewards = 0
        total_reward = 0
        signers = 0
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                signers = signers + 1
                # block reward of the validator
                shard_metrics = i['metrics']['by-bls-key']
                validator_reward = 0
                for by_shard in shard_metrics:
                    validator_addr = by_shard['key']['earning-account']
                    by_shard_reward = block_reward * float(by_shard['key']['overall-percent']) / 0.32
                    validator_reward = validator_reward + by_shard_reward

                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_curr[address] = reward_accumulated
                reward = reward_accumulated
                if address not in acc_rewards_prev:
                    continue
                reward = reward_accumulated - acc_rewards_prev[address]
                # this reward should match sum of delegation rewards
                ds = i['validator']['delegations']
                del_rewards = 0
                dels = delegations_prev[address]
                for d in ds:
                    d_addr = d['delegator-address']
                    d_reward = d['reward']
                    del_rewards = del_rewards + d_reward
                    if d_addr in dels:
                        del_rewards = del_rewards - dels[d_addr] 
                if del_rewards != reward:
                    logger.warning(f"Test-R7: Fail")
                    logger.warning(f"for validator {address}, expected block reward, {validator_reward}, validator block reward, {reward}, delegation reward, {del_rewards}")
                flag = False
                
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = R8_test
    if flag:
        logger.info(f"Test-R7: Succeed")
        return True
    else:
        return False

def R8_test():
    global curr_test
    logger.info(f"Test-R8: Block reward inversely proportional to staked amount")
    num = 2 #need at least two blocks to compare, rerun the test!
    try:
        if num < 2:
            logger.info(f"need at least two blocks to compare, rerun the test!")
            curr_test = R9_test
            return

        block, last_block = getCurrentAndLastBlock()
        while last_block - block > 32:
            block = getBlockNumber()
        if block == last_block:
            logger.info(f"current at the last block, wait until the 6th block in the new epoch")
            while block < last_block+6:
                block = getBlockNumebr()
        logger.info(f"current block {block}, will begin collecting infos...")
        
        acc_rewards_prev = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_prev[address] = reward_accumulated

        next_block = block + 1
        while block < next_block:
            block = getBlockNumber()
        logger.info(f"new block reached, {block}, will begin testing...")
        block_reward = dict()
        block_stake = dict()

        iterations = 0
        flag = True
        while iterations < num:
            logger.info(f"current block, {current_block}")
            # staked amount
            staked = getStakedAmount()
            block_stake[current_block] = staked
            # get the validator info and compute validator rewards
            acc_rewards_curr = dict()
            delegations_curr = dict()
            validator_infos = getAllValidatorInformation()
            total_reward = 0
            for i in validator_infos:
                if i['currently-in-committee'] == True:
                    address = i['validator']['address']
                    reward_accumulated = i['lifetime']['reward-accumulated']
                    acc_rewards_curr[address] = reward_accumulated
                    reward = reward_accumulated
                    if address not in acc_rewards_prev:
                        continue
                    reward = reward_accumulated - acc_rewards_prev[address]
                    total_reward = total_reward + reward

            block_reward[current_block] = total_reward

            last_block = current_block
            current_block = getBlockNumber()
            while current_block == last_block:
                current_block = getBlockNumber()

            acc_rewards_prev = acc_rewards_curr
            delegations_prev = delegations_curr

            iterations = iterations + 1

        logger.info(f"size: {len(block_stake)}, {len(block_reward)}")
        # reward increasing
        sorted_reward = sorted(block_reward.items(), key=lambda kv: kv[0], reverse = False)
        # stake should remain same or decrease
        sorted_stake = sorted(block_stake.items(), key=lambda kv: kv[0], reverse = False)

        for i in range(len(sorted_reward)-1):
            next_reward = sorted_reward[i+1][1]
            next_stake = sorted_stake[i+1][1]
            if (next_reward > curr_reward and next_stake > curr_stake) or (next_reward < curr_reward and next_stake < curr_stake):
                logger.warning(f"Test-R8: Fail")
                logger.warning(f"block reward is not inversely proportional to stake")
                flag = False
            curr_stake = next_stake
            curr_reward = next_reward
        
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = R9_test
    if flag:
        logger.info("Test-R8: Succeed")
        return True
    else:
        return False

def R9_test():
    global curr_test
    logger.info(f"Test-R9: Block reward never drops below minimum or raises above maximum block reward")
    num = 1
    try:
        current_block = getBlockNumber()
        next_block = current_block + 1
        logger.info(f"current block: {current_block}, will begin collecting infos...")
        acc_rewards_prev = dict()
        validator_infos = getAllValidatorInformation()
        for i in validator_infos:
            if i['currently-in-committee'] == True:
                address = i['validator']['address']
                reward_accumulated = i['lifetime']['reward-accumulated']
                acc_rewards_prev[address] = reward_accumulated
        logger.info(f"new block reached: {current_block}, will begin testing...")        
        current_block = getBlockNumber()
        while current_block < next_block:
            current_block = getBlockNumber()

        # per-shard
        # default reward = 18 ONEs
        # min reward = 0, when >= 80% staked instead of 35% (of the circulating supply)
        # max reward = 32, when ~0% staked instead of 35% (of the circulating supply)
        # so, for four shards, (min, max) = (0, 128)
        min_total_reward = 0
        max_total_reward = 128e18

        iterations = 0
        flag = True
        while iterations < num:
            logger.info(f"current block: {current_block}")

            # get the validator info and compute validator rewards
            acc_rewards_curr = dict()
            validator_infos = getAllValidatorInformation()
            total_reward = 0
            for i in validator_infos:
                if i['currently-in-committee'] == True:
                    address = i['validator']['address']
                    reward_accumulated = i['lifetime']['reward-accumulated']
                    acc_rewards_curr[address] = reward_accumulated
                    if address not in acc_rewards_prev:
                        continue
                    reward = reward_accumulated - acc_rewards_prev[address]
                    total_reward = total_reward + reward   

            if total_reward < min_total_reward or total_reward > max_total_reward:
                logger.warning(f"Test R9: Fail")
                logger.warning(f"block reward below minimum or above maximum, block reward: {total_reward}, minimum: {min_total_reward}, maximum: {max_total_reward}")
                flag = False
            last_block = current_block
            current_block = getBlockNumber()
            while current_block == last_block:
                current_block = getBlockNumber()

            acc_rewards_prev = acc_rewards_curr
            iterations = iterations + 1
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = R11_test    
    if flag:
        logger.info(f"Test R9: Succeed")
        return True
    else:
        return False
    
def R11_test():
    global curr_test
    logger.info(f"Test-R11: Earning is proportional to effective stake ")
    num = 1
    iterations = 0
    curr_test = R14_test
    try:
        while iterations < num:
            logger.info(f"test, {iterations+1} will begin ...")
            block, last_block = getCurrentAndLastBlock()
            if block == last_block:
                new_block = block+1
                while block < new_block:
                    block = getBlockNumber()
            block, last_block = getCurrentAndLastBlock()
            epoch = getEpoch()

            second_last_block = last_block - 1
            while block < second_last_block:
                block = getBlockNumber()
            logger.info(f"second last block in current epoch reached {block}, will begin testing...")
            stakes, aprs = getStakesAndAprs()

            # in the last block, we can not get the total effective stakes, no metrics. 
            new_block = block + 2
            while block < new_block:
                block = getBlockNumber()
            logger.info(f"first block in new epoch reached, {block}, will compare the changes")
            new_stakes, new_aprs = getStakesAndAprs()

            apr_diff = diffAndFilter(aprs, new_aprs)
            # get the validators whose effective stake changes
            stake_diff = diffAndFilter(stakes, new_stakes)

            if not stake_diff:
                logger.info(f"in this iteration, no validators change the effective stake")
                return "Need More Tests"
            if not apr_diff:
                logger.info(f"in this iteration, no validators change the apr")
                return "Need More Tests"

            flag = True
            for k,v in stake_diff.items():
                if k in apr_diff:
                    if v > 0: 
                        if apr_diff[k] <= 0:
                            flag = False
                            logger.warning(f"Test-R11: Fail")
                            logger.warning(f"{k}'s effective stake increase: {v}")
                            logger.warning(f"but apr doesn't increase, apr changes: {apr_diff[k]}")
                    if v < 0:
                        if apr_diff[k] >= 0:
                            flag = False
                            logger.warning(f"Test-R11: Fail")
                            logger.warning(f"{k}'s effective stake decrease: {v}")
                            logger.warning(f"apr doesn't decrease, apr changes: {apr_diff[k]}")
            iterations += 1 
    except TypeError as e:
        logger.error(f"error: {e}")
        
    if flag:
        logger.info(f"Test-R11: Succeed")
        return True
    else:
        return False
    
def R14_test():
    global curr_test
    logger.info(f"Test-R14: Shard fairness: rate of earning on shards is similar if the block time are same")
    num = 1
    iterations = 0
    try:
        while iterations < num:
            block = getBlockNumber()
            logger.info(f"current block number, {block}")
            next_block = block + 1
            while block < next_block:
                block = getBlockNumber()
            # get the average apr for each shard 
            logger.info(f"next block reached, {block}, will begin testing")
            apr_avg = getAprByShards()
            apr_avg = sorted(apr_avg.items(), key=lambda kv: kv[0])
            logger.info(f"the average apr for each shard: {apr_avg}")
            iterations += 1  
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = CN1_test
    return "Need Manually Check"

def CN1_test():
    global curr_test
    logger.info(f"Test-CN1: Slow validator is never starved (should be able to sign blocks)")
    try:
        block, last_block = getCurrentAndLastBlock()
        logger.info(f"waiting for the last second block...")
        while block < last_block-1:
            block = getBlockNumber()
        logger.info(f'the last second block reached, will check signing percentage')
        # get the validator's reward who just meets the 2/3 cut-off  
        cutoff_rewards = getAvailabilityAndRewards()


        new_block = block + 1
        while block < new_block:
            block = getBlockNumber()
        logger.info(f"last block reached, {block}, will begin testing")
        next_rewards, status = getRewardsAndStatus(cutoff_rewards)
        flag = True
        for k,v in next_rewards.items():
            reward_per_block = v - cutoff_rewards[k]
            if reward_per_block == 0 or status[k] == 'not eligible to be elected next epoch':
                flag = False
                logger.warning(f"Test-CN1: Fail")
                if reward_per_block == 0:
                    logger.warning(f"Slow validator doesn't get reward")
                if status[k] == 'not eligible to be elected next epoch':
                    logger.warning(f"Slow validator is no longer eligible")
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = U1_test
    if flag:
        logger.info(f"Test-CN1: Succeed")
        return True
    else:
        return False

def U1_test():
    global curr_test
    logger.info("Test-U1: Delegator/validator stake locked until undelegate")
    num = 1
    try:
        block, last_block = getCurrentAndLastBlock()
        if block + num > last_block:  
            logger.info(f"wait until new epoch starts ...")
            new_block = last_block + 1
            while block < new_block:
                block = getBlockNumber()
        iterations = 0
        flag = True
        total_reduce_num = 0
        while iterations < num:
            epoch = getEpoch()
            logger.info(f"current epoch number, {epoch}, current block number, {block}, will begin testing...")
            stake, undelegate = getStakeAndUndelegate2(epoch)
            next_block = block + 1
            while block < next_block:
                block = getBlockNumber()
            epoch = getEpoch()
            logger.info(f"next block reached, {block}, current epoch, {epoch}, will compare the stakes")
            new_stake, new_undelegate = getStakeAndUndelegate2(epoch)
            diff_stake = diffAndFilter2(stake, new_stake)
            diff_undelegate = diffAndFilter2(undelegate, new_undelegate)

            reduce_num = 0
            for key, val in diff_stake.items():
                for k,v in diff_stake[key].items():
                    if v < 0:
                        reduce_num += 1
                        total_reduce_num +=1
                        if diff_undelegate[key][k] <= 0:
                            logger.warning(f"Test-U1: Fail")
                            logger.warning(f"Delgeator stake reduces without undelegate")
                            logger.warning(f"undelegate changes:  {diff_undelegate[key][k]}")
                            logger.warning(f"stake changes: {v}")
                            flag = False        
            if reduce_num == 0:
                logger.info(f"No stake reduces at current test, need more tests")
            iterations += 1  
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = U2_test
    if total_reduce_num == 0:
        return "Need More Tests"
    if flag:
        logger.info(f"Test-U1: Succeed")
        return True
    if not flag:
        return False

def U2_test():
    global curr_test
    logger.info(f"Test-U2: After undelegate, the total stake amount for that validator should subtract the undelegation amount before next epoch")
    num = 1
    iterations = 0
    flag = True
    try:
        while iterations < num:
            block, last_block = getCurrentAndLastBlock()
            # need at least 2 blocks left to compare difference
            if block == last_block:
                new_block = last_block + 1
                while block < new_block:
                    block = getBlockNumber()
                block, last_block = getCurrentAndLastBlock()
            epoch = getEpoch()
            logger.info(f"current epoch numebr: {epoch}, block number: , {block}, will begin testing...")
            stake, undelegate = getStakeAndUndelegate(epoch)

            while block < last_block:
                block = getBlockNumber()
            logger.info(f"last block number reaches, {block}, will compare the stakes and undelegations")
            new_stake, new_undelegate = getStakeAndUndelegate(epoch)
            diff_stake = diffAndFilter(stake, new_stake)
            diff_undelegate = diffAndFilter(undelegate, new_undelegate)

            if not diff_undelegate:
                logger.info(f"no undelegation happens in current test, need more tests")

            for k,v in diff_undelegate.items():
                if k in diff_stake:
                    if v != -(diff_stake[k]):
                        logger.warning(f"Test-U2: Fail")
                        logger.warning(f"Validator {k}: the stake change doesn't meet the undelegation change")
                        flag = False
                else:
                    logger.warning(f"Test-U2: Fail")
                    logger.warning(f"Validator: {k}: total stakes doesn't change after undelegation")
                    flag = False
            iterations += 1 
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = S1_test
    if flag:
        logger.info("Test-U2: Succeed")
        return True
    else:
        return False

def S1_test():
    global curr_test
    logger.info(f"Test-S1: Equilibrium: percentage of external validators on each shard is balanced")
    try:
        committees = getCommittees()['quorum-deciders']
        perc = dict()
        for k,v in committees.items():
            members = v['committee-members']
            count = v['count']
            num = 0
            for i in members:
                if not i['is-harmony-slot']:
                    num += 1
            perc[k] = num/count
        logger.info(f"the percentage for each shard: ", perc)
    except TypeError as e:
        logger.error(f"error: {e}")
        
    curr_test = S6_test
    return "Need Manually Check"

def S6_test():
    global curr_test
    logger.info(f"Test-S6: Total staked tokens cannot exceed circulating supply")
    num = 1
    try:        
        current_block = getBlockNumber()
        iterations = 0
        flag = True
        while iterations < num:
            logger.info(f"current block, {current_block}")
            supply, stake = getStakingMetrics()

            logger.info(f"supply: {supply}")
            logger.info(f"stake: {stake}")

            if stake > supply:
                logger.warning(f"Test-S6: Fail")
                logger.warning(f"stake is higher than supply. stake: {stake}, supply: {supply}")
                flag = False
            last_block = current_block
            current_block = getBlockNumber()
            while current_block == last_block:
                current_block = getBlockNumber()
            iterations = iterations + 1
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = S7_test
    if flag:    
        logger.info("Test-S6: Succeed")
        return True
    else:
        return False

def S7_test():
    global curr_test
    logger.info(f"Test-S7: Stake is equally distributed across slots")
    num = 1
    try:        
        current_block = getBlockNumber()
        iterations = 0
        flag = True
        while iterations < num:
            counters = [0, 0, 0, 0]
            effect_stakes = [0.0, 0.0, 0.0, 0.0]
            logger.info(f"current block: {current_block}")

            validator_infos = getAllValidatorInformation()
            total_reward = 0
            for i in validator_infos:
                if i['metrics']:
                    addr = i['validator']['address']
                    by_shard_metrics = i['metrics']['by-bls-key']
                    e_stake = float(by_shard_metrics[0]['key']['effective-stake'])
                    for by_shard_metric in by_shard_metrics:
                        stake = float(by_shard_metric['key']['effective-stake'])
                        if stake != e_stake:
                            logger.warning(f"Test-S7: Fail")
                            logger.warning(f"for validator {addr}")
                            flag = False
            last_block = current_block
            current_block = getBlockNumber()
            while current_block == last_block:
                current_block = getBlockNumber()
            iterations = iterations + 1
    except TypeError as e:
        logger.error(f"error: {e}")
    curr_test = None    
    if flag:
        logger.info(f"Test-S7: Succeed")
        return True
    else:
        return False
    
def M4_test():
    global no_external_test
    logger.info(f"Test-M4: Zero median when no external validators")
    no_external_test = R13_test
    try:
        if not getAllValidatorInformation():
            median = getEposMedian()
            if median != 0:
                logger.warning(f"Test-M4: Fail")
                logger.warning(f"epos median when no external validators: {median}")
            else:
                logger.info(f"Test-M4: Succeed")
        else:
            logger.info(f"currently there are external validators, doesn't meet the testing needs")
            return "Need More Tests"
    except TypeError as e:
        logger.error(f"error: {e}")
    

def R13_test():
    global no_external_test
    logger.info(f"Test-R13: In case of no external validators, no block reward is given out")
    try:
        committees = getCommittees()
        testing_status = True
        for k,v in committees['quorum-deciders'].items():
            for i in v['committee-members']:
                if not i['is-harmony-slot']:
                    testing_status = False
                    logger.info(f"currently there are external validators, doesn't meet the testing needs")
                    no_external_test = None
                    return "Need More Tests"
        no_external_test = None
        if not getAllValidatorInformation():
            logger.info(f"Test-R13: Succeed")
            return True
        else:
            logger.warning(f"Test-R13: Fail")
            logger.warning(f"there is block reward when no external validators")
            return False
    except TypeError as e:
        logger.error(f"error: {e}")
        
if __name__ == "__main__":
    curr_test = E1_test
    success = 0
    fail = 0
    more = 0
    manual = 0
    error = 0
    count = 0
    fail_lst = []
    more_lst = []
    check_lst = []
    error_lst = []
    while curr_test:
        test_name = curr_test.__name__
        logger.info(f"\n{'=' * 15} Starting {test_name} {'=' * 15}\n")                        
        res = curr_test() 
        if res == True:
            success += 1
        elif res == False:
            fail += 1
            fail_lst.append(test_name)
        elif res == 'Need More Tests':
            more += 1
            more_lst.append(test_name)
        elif res == 'Need Manually Check':
            manual += 1
            check_lst.append(test_name)
        else:
            error += 1
            error_lst.append(test_name)
        count += 1
        
    no_external_test = M4_test
    while no_external_test:
        test_name = no_external_test.__name__
        logger.info(f"\n{'=' * 15} Starting {test_name} {'=' * 15}\n")
        res = no_external_test() 
        if res == True:
            success += 1
        elif res == False:
            fail += 1
            fail_lst.append(test_name)
        elif res == 'Need More Tests':
            more += 1
            more_lst.append(test_name)
        elif res == 'Need Manually Check':
            manual += 1
            check_lst.append(test_name)
        else:
            error += 1
            error_lst.append(test_name)
        count += 1
    logger.info(f"\n{'=' * 25} Test Results {'=' * 25}\n")
    logger.info(f"Total Tests: {count}")
    logger.info(f"Successful Tests: {success}")
    logger.info(f"Failed Tests: {fail}")
    if fail_lst:
        logger.info(f"{fail_lst}")
    logger.info(f"Test doesn't meet requirements, need more tests: {more}")
    if more_lst:
        logger.info(f"{more_lst}")
    logger.info(f"Need to manual check: {manual}")
    if check_lst:
        logger.info(f"{check_lst}")
       

