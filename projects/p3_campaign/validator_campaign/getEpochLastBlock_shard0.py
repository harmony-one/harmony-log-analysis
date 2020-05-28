#!/usr/bin/env python
# coding: utf-8

import requests
import json
import os
from os import path

def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json; charset=utf8'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
    except requests.exceptions.ConnectionError as e:
        print("Error: connection error")
        time.sleep(10)
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

def epochLastBlock(epoch) -> list:
    url = "http://localhost:9500"
    method = "hmy_epochLastBlock"
    params = [epoch]
    return get_information(url, method, params)

def getLatestHeader() -> dict:
    url = "http://localhost:9500"
    method = 'hmy_latestHeader'
    params = []
    return get_information(url, method, params)

if __name__ == "__main__":

    base = path.dirname(path.realpath(__file__))
    json_dir = path.abspath(path.join(base, '..', 'json'))
    
    if not path.exists(json_dir):
        try:
            os.mkdir(json_dir)
        except:
            print("Could not make json directory")
            exit(1)
    
    latest = getLatestHeader()
    if latest != None:
        end_num = latest['result']['epoch']
    epoch_last = []
    for i in range(0, end_num+1):
        res = epochLastBlock(i)
        if res != None:
            epoch_last.append({
                "epoch": i,
                "last-block": res['result']
                })
        
    with open(path.join(json_dir, "epochLastBlock_shard_0.json"), 'w') as f:
        json.dump(epoch_last, f, indent = 4)
    print("save last block of every epoch to {}/epochLastBlock_shard_0.json".format(json_dir)) 
