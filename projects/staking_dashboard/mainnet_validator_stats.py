#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import json
import datetime
import time
import os
import gspread
from os import path

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

def getAllValidatorInformation():
    url = 'https://api.s0.t.hmny.io/'
    method = 'hmy_getAllValidatorInformation'
    params = [-1]
    return get_information(url, method, params)

def getEpoch():
    url = 'https://api.s0.t.hmny.io/'
    method = "hmy_getEpoch"
    params = []
    epoch = get_information(url, method, params)
    return int(epoch, 16)

def getBlockNumber():
    url = 'https://api.s0.t.hmny.io/'
    method = "hmy_blockNumber"
    params = []
    num = get_information(url, method, params)
    return int(num, 16)

if __name__ == "__main__":  
    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'csv'))
    data = path.join(data, 'mainnet_validator')
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make csv directory")
            exit(1)
    
    while True:
        epoch = getEpoch()
        block = getBlockNumber()
        print("-- Start Data Processing --")
        # get the total validator number
        val_infos = getAllValidatorInformation()
        address = []
        name = []
        apr = []
        uptime = []
        stake = []
        self_stake = []
        rate = []
        epos_status = []
        boot_status = []
        for i in val_infos:
            address.append(i['validator']['address'])
            name.append(i['validator']['name'])
            apr.append("{0:.2f}%".format(float(i['lifetime']['apr'])*100))
            sign_info = i['lifetime']['blocks']
            if float(sign_info['to-sign']) != 0:
                sign_perc = float(sign_info['signed'])/float(sign_info['to-sign'])
                uptime.append("{0:.2f}%".format(sign_perc*100))
            else:
                uptime.append(None)    
            stake.append(int(float(i['total-delegation'])/1e18))
            self_stake.append(i['validator']['delegations'][0]['amount']/1e18)
            rate.append("{0:.2f}%".format(float(i['validator']['rate'])))
            epos_status.append(i['epos-status'])
            boot_status.append(i['booted-status'])
        df = pd.DataFrame(list(zip(address, name, apr, stake, self_stake, rate, uptime, epos_status, boot_status)), columns =['address', 'name', 'apr', 'total-stake', 'self-stake', 'fees', 'uptime', 'epos-status','boot_status'])

#         timestamp = datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S") 
        print("-- Save csv files to ./csv/mainnet_validator/{}_{}_validator.csv --".format(epoch,block))
        df.to_csv(path.join(data, '{}_{}_validator.csv'.format(epoch, block)), index = False)
        gc = gspread.service_account('/home/ubuntu/jupyter/harmony-log-analysis/projects/staking_dashboard/credential/jsonFileFromGoogle.json')
        sh = gc.open("harmony-mainnet-tracker")
        worksheet = sh.worksheet("validator-tracker")
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        df['uptime'] = df['uptime'].apply(lambda c: float(c.replace("%",""))/100 if type(c) == str else c)
        filter_df = df[(df['epos-status'] == 'not eligible to be elected next epoch') & (df['uptime'] > 0.8)]
        filter_df.reset_index(drop = True, inplace = True)
        print("-- Save csv files to ./csv/mainnet_validator/{}_{}_filter_validator.csv --".format(epoch,block))
        filter_df.to_csv(path.join(data, '{}_{}_filter_validator.csv'.format(epoch, block)), index = False)
        worksheet = sh.worksheet("filter-validator-tracker")
        worksheet.update([filter_df.columns.values.tolist()] + filter_df.values.tolist())
        
        curr_epoch = getEpoch()
        while epoch == curr_epoch:
            time.sleep(7200)
            curr_epoch = getEpoch()
 