#!/usr/bin/env python
# coding: utf-8

import json
import requests
from datetime import datetime
import pandas as pd

def get_information(method, params):
    url = 'https://api.s0.os.hmny.io/'
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    content = json.loads(r.content)
    return content['result']

def getBlockByNumber(number):
    method = 'hmyv2_getBlockByNumber'
    params = [number, {"fullTx":True,"inclTx":True,"InclStaking":True}]
    return get_information(method, params)

if __name__ == "__main__":
    transactions = []
    staking = []
    time = []
    for i in range(40765, 51046):
        res = getBlockByNumber(i)
        transactions.append(len(res['transactions']))
        time.append(datetime.fromtimestamp(res['timestamp']))
        staking.append(len(res['stakingTransactions']))

    df = pd.DataFrame(list(zip(time, transactions, staking)), columns = ['time', 'transactions', 'staking-transactions'])
    df.to_pickle("2020_04_19_mainnet.pkl")
    print("successfully save the dataframe to pickle")

