#!/usr/bin/env python
# coding: utf-8

import json
import requests
import argparse
from datetime import datetime


def get_information(url, method, params) -> dict:
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
    except:
        print("Error: request meets error")
        time.sleep(5)
        return None
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None
    try:
        content = json.loads(r.content)
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None
    if "result" in content:
        return content['result']
    else:
        print("Error: The method does not exist/is not available")
        return None


def getBlockByNumber(number) -> dict:
    url = "http://localhost:9500"
    method = 'hmy_getBlockByNumber'
    params = [hex(number), False]
    return get_information(url, method, params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_block', required = True, help = 'The block number you want to start querying')
    args = parser.parse_args()
    new_num = num = int(args.start_block)
    res = getBlockByNumber(num)
    timestamp = int(res['timestamp'], 16)
    new_time = time = datetime.fromtimestamp(timestamp)
    target = datetime.strptime("2020_05_08 17:00:00", '%Y_%m_%d %H:%M:%S')
    diff = (target - time).seconds

    while time.strftime('%Y_%m_%d %H:%M:%S') < '2020_05_08 17:10:00':
        res = getBlockByNumber(num+1)
        if res != None:
            time = datetime.fromtimestamp(int(res['timestamp'],16))
        if target > time:
            new_diff = (target - time).seconds
        else:
            new_diff = (time-target).seconds
        if new_diff < diff:
            new_num = num+1
            new_time = time
            diff = new_diff
        num += 1
    print(f"The closest block number to {target.strftime('%Y_%m_%d %H:%M:%S')} is {new_num}, cloest time is {new_time}")
