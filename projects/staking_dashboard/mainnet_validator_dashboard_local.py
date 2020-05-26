#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
import os
from os import path
import time
import requests
import re
from collections import defaultdict

def get_size(size):
    html_url = "https://staking-explorer2-268108.appspot.com/networks/harmony/validators_with_page?active=false&page=0&search=&size={}&sortOrder=desc&sortProperty=apr".format(size)
    res = requests.get(html_url)
    content = json.loads(res.content)
    return content['total']


def get_validator(page, size):
    html_url = "https://staking-explorer2-268108.appspot.com/networks/harmony/validators_with_page?active=false&page={}&search=&size={}&sortOrder=desc&sortProperty=apr".format(page, size)
    res = requests.get(html_url)
    content = json.loads(res.content)
    return content['validators']

if __name__ == "__main__":  
    # get uptime
    size = get_size(1)
    pages = size // 100 + 1
    # get the validator info
    validator = []
    for i in range(pages):
        val = get_validator(i,100)
        validator.extend(val)
        
    column = list(validator[0].keys())
    remove = ['bls-public-keys','delegations','last-epoch-in-committee','update-height','remainder','voting_power','signed_blocks','blocks_should_sign','uctDate','index','commision-recent-change','average_stake','average_stake_by_bls','active']
    new_column = []
    for i in column:
        if i not in remove:
            new_column.append(i)
    df = pd.DataFrame(validator, columns = new_column)
    percent_change = ['rate','max-rate','max-change-rate', 'apr','uptime_percentage']
    for name in percent_change:
        df[name] = df[name].apply(lambda c: "{0:.2f}%".format(float(c)*100))
    atto_change = ['min-self-delegation','max-total-delegation', 'self_stake', 'total_stake', 'lifetime_reward_accumulated']
    for name in atto_change:
        df[name] = df[name].apply(lambda c: float(c)/1e18)
    df.to_csv('../csv/validator_info_mainnet.csv', index = False)
    print(f"csv file saved in ../csv/validator_info_mainnet.csv")