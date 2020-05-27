#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import threading
import json
import datetime
import time
import os

def get_size(size):
    html_url = "https://staking-explorer2-268108.appspot.com/networks/harmony-open-staking/validators_with_page?active=true&page=0&search=&size={}&sortOrder=desc&sortProperty=expectedReturns".format(size)
    headers={
            u'accept': u'application/json, text/plain, */*',
            u'accept-encoding': u'gzip, deflate, br',
            u'accept-language': u'en-US,en;q=0.9',
            u'if-none-match': u'W/"799e-JHamRgkDvpeHfY2B0sqlqnbx35E"',
            u'origin': u'https://staking.harmony.one',
            u'referer': u'https://staking.harmony.one/validators',
            u'sec-fetch-dest': u'empty',
            u'sec-fetch-mode': u'cors',
            u'sec-fetch-site': u'cross-site',
            u'user-agent': u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/80.0.3987.132 Safari/537.36'
            }

    res = requests.get(html_url, headers=headers)
    content = json.loads(res.content)
    return content['total']

def get_validator(page, size):
    html_url = "https://staking-explorer2-268108.appspot.com/networks/harmony-open-staking/validators_with_page?active=false&page={}&search=&size={}&sortOrder=desc&sortProperty=expectedReturns".format(page, size)
    headers={
            u'accept': u'application/json, text/plain, */*',
            u'accept-encoding': u'gzip, deflate, br',
            u'accept-language': u'en-US,en;q=0.9',
            u'if-none-match': u'W/"38ad7-CgwfOgtbRPv9+zY+XmhKsvEBDDM"',
            u'origin': u'https://staking.harmony.one',
            u'referer': u'https://staking.harmony.one/validators',
            u'sec-fetch-dest': u'empty',
            u'sec-fetch-mode': u'cors',
            u'sec-fetch-site': u'cross-site',
            u'user-agent': u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/80.0.3987.132 Safari/537.36'
            }

    res = requests.get(html_url, headers=headers)
    content = json.loads(res.content)
    return content['validators']

def daily_monitor():

    global old_del
    global old_val
    # get the new total validator number
    curr_val = get_size(1)
    new_val = curr_val - old_val
    print("Number of New Validators: " + str(new_val))

    pages = curr_val // 100 + 1
    # get the validator info
    validator = []
    for i in range(pages):
        val = get_validator(i,100)
        validator.extend(val)

    df = pd.DataFrame(validator, columns = ['address', 'creation-height','update-height','self_stake','total_stake','delegations'])
    df['delegator_num'] = df.apply(lambda c: len(c['delegations']), axis = 1)
    df['delegator_stake'] = df['total_stake'] - df['self_stake']
    df.drop(['delegations'], axis = 1, inplace = True)

    # do we need to remove self-delegate part
    curr_del = df['delegator_num'].sum()
    new_del = curr_del - old_del
    print("Number of New Delegators: " + str(new_del))

    # store info into csv file
    now = datetime.datetime.now()
    date_time = now.strftime("%m-%d-%Y, %H:%M:%S")
    fig_dir = "../../csv/staking_dashboard/"
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)
    df.to_csv(fig_dir + date_time + '_validator_info.csv', index=False)

    # reset old data
    old_val, old_del = curr_val, curr_del

if __name__ == "__main__":
    old_val = 0
    old_del = 0
    while True:
        now = datetime.datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        if now.hour == 10 and now.minute == 26:
            print("Current Date and Time:",date_time)
            daily_monitor()
            print("wait for 24 hours to get update")
            print("")
        time.sleep(60)
