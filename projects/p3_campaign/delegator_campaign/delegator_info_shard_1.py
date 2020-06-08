#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
from os import path
from collections import defaultdict
from threading import Thread
import pyhmy
from pyhmy import (
        blockchain,
        account
        )

if __name__ == "__main__":

    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'csv'))
    data = path.join(data, 'mainnet_delegator')
    if not path.exists(data):
        try:
            os.makedirs(data)
        except:
            print("Could not make csv directory")
            exit(1)

    print("-- Start Data Processing --")
    print(f"Current Epoch number: 196, Block number: 94941")
    df = pd.read_csv("csv/mainnet_delegator/shard_0_delegator.csv", index_col=0)

    balance = defaultdict(float)
    txs_sum = defaultdict(float)
    address_lst = df['address'].tolist()
#     address_lst.remove("one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur")
    thread_lst = defaultdict(list)
    for i in range(len(address_lst)):
        thread_lst[i%25].append(i)
    def collect_data(x):
        global balance
        for i in thread_lst[x]:
            addr = address_lst[i]
            res = account.get_balance_by_block(addr, 94941)
            if res != None:
                balance[addr] += res/1e18
    threads = []
    for x in range(25):
        threads.append(Thread(target = collect_data, args = [x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    thread_lst = defaultdict(list)
    for i in range(94942):
        thread_lst[i%50].append(i)

    def collect_data(x):
        global txs_sum
        for i in thread_lst[x]:
            transactions = blockchain.get_block_by_number(i, include_full_tx=True)['transactions']
            for txs in transactions:
                if txs['from'] in address_lst:
                    addr = txs['from']
                    txs_sum[addr] -= int(txs['value'],16)/1e18
                if txs['to'] in address_lst:
                    addr = txs['to']
                    txs_sum[addr] += int(txs['value'],16)/1e18
    threads = []
    for x in range(50):
        threads.append(Thread(target = collect_data, args = [x]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    balance_df = pd.DataFrame(balance.items(), columns=['address', 'balance_shard_1'])
    txs_sum_df = pd.DataFrame(txs_sum.items(), columns=['address', 'txs_sum_shard_1'])

    df = df.join(balance_df.set_index('address'), on = 'address')
    df = df.join(txs_sum_df.set_index('address'), on = 'address')
    # df['total-lifetime-reward'] = df['current-reward'] + df['balance'] + df['total-stake'] + df['pending-undelegation'] - df['txs_sum']

    print("-- Filter the delegators in the google sheet --")
    # html = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDAqXO-xVP4UwJlNJ6Qaws4N-TZ3FNZXqiSidPzU1I8pX5DS063d8h0jw84QhPmMDVBgKhopHhilFy/pub?gid=0&single=true&output=csv'
    # delegator = read_csv(html)
    # df['filter'] = df.apply(lambda c: True if c['address'] in delegator else False, axis = 1)
    print("-- Save csv files to ./csv/mainnet_delegator/shard_1_delegator.csv --")
    df.to_csv(path.join(data, 'shard_1_delegator.csv'))

    # filter_df = df[df['filter']].reset_index(drop = True)
    # filter_df.to_csv(path.join(data, 'shard_1_filter_delegator.csv'))
    # print("-- Save csv files to ./csv/mainnet_delegator/shard_1_filter_delegator.csv --")
