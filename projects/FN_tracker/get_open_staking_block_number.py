#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import requests
import json

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json; charset=utf8'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
    except requests.exceptions.ConnectionError as e:
        print("Error: connection error")
        time.sleep(5)
        return None
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        r.json()
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    return r.json()

def getBlockByNumber(shard, number) -> dict:
    url = endpoint[shard]
    method = 'hmy_getBlockByNumber'
    params = [hex(number), False]
    return get_information(url, method, params)['result']

if __name__ == "__main__":
    endpoint = ['https://api.s0.t.hmny.io/', 'https://api.s1.t.hmny.io/', 'https://api.s2.t.hmny.io/', 'https://api.s3.t.hmny.io/']
    mainnetEpochBlock1 = 344064
    blocksPerEpoch = 16384
    block_num_0 = 16384*185+344064 #3375104

    time = int(getBlockByNumber(0, block_num_0)['timestamp'],16)
    print(f"shard 0, block number {block_num_0}, time {datetime.fromtimestamp(time).strftime('%Y_%m_%d_%H:%M:%S')}")

    block_num_1 = 3286736
    time = int(getBlockByNumber(1, block_num_1)['timestamp'],16)
    print(f"shard 1, block number {block_num_1}, time {datetime.fromtimestamp(time).strftime('%Y_%m_%d_%H:%M:%S')}")


    block_num_2 = 3326152
    time = int(getBlockByNumber(2, block_num_2)['timestamp'],16)
    print(f"shard 2, block number {block_num_2}, time {datetime.fromtimestamp(time).strftime('%Y_%m_%d_%H:%M:%S')}")

    block_num_3 = 3313571
    time = int(getBlockByNumber(3, block_num_3)['timestamp'],16)
    print(f"shard 3, block number {block_num_3}, time {datetime.fromtimestamp(time).strftime('%Y_%m_%d_%H:%M:%S')}")