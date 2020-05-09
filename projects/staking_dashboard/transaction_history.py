#!/usr/bin/env python
# coding: utf-8

import json
import requests
import pandas as pd
import datetime
import os
from os import path
import argparse

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    r = requests.post(url, headers=headers, data = json.dumps(data))
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        content = json.loads(r.content)
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    
    if "error" in content:
        print("Error: The method does not exist/is not available")
        return None
    else:
        return content['result']


def getNormalTransaction(shard, address):
    url = endpoint[shard]
    method = "hmyv2_getTransactionsHistory"
    params = [{
        "address": address,
        "fullTx": True,
        "pageIndex": 0,
        "pageSize": 100000,
        "txType": "ALL",
        "order": "ASC"
    }]
    return get_information(url, method, params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', required = True, help = 'ONE address to query from')
    parser.add_argument('--name', required = True, help = 'Your Name who is query from')
    args = parser.parse_args()
    endpoint = ['https://api.s0.os.hmny.io/', 'https://api.s1.os.hmny.io/', 'https://api.s2.os.hmny.io/', 'https://api.s3.os.hmny.io/']
    addr = args.address
    name = args.name

    base = path.dirname(path.realpath(__file__))
    csv = path.abspath(path.join(base, 'csv'))
    if not path.exists(csv):
        try:
            os.makedirs(csv)
        except:
            print("Could not make data directory")
            exit(1)
    print("===== Start Data Processing =====")
    res = []
    for i in range(len(endpoint)):
        txs = getNormalTransaction(i, addr)
        if txs != None:
            res.extend(txs['transactions'])
    df = pd.DataFrame.from_dict(res, orient='columns')
    df['timestamp'] = df['timestamp'].apply(lambda c: datetime.datetime.fromtimestamp(c))
    df['value'] = df['value'].apply(lambda c: int(c/1e18))
    txs = df[['timestamp','from','to','value']]
    txs.to_csv(path.join(csv, f'{name}_transaction.csv'))
    print("csv successfully save to ./csv/{}_transaction.csv".format(name))

