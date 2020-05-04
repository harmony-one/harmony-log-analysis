#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import requests
import pandas as pd
import datetime


# In[2]:


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


# In[3]:


def getNormalTransaction(shard, address):
    url = endpoint[shard]
    method = "hmyv2_getTransactionsHistory"
    params = [{
        "address": address,
        "fullTx": True,
        "pageIndex": 0,
        "pageSize": 10000,
        "txType": "ALL",
        "order": "ASC"
    }]
    return get_information(url, method, params)


# In[4]:


endpoint = ['https://api.s0.os.hmny.io/', 'https://api.s1.os.hmny.io/', 'https://api.s2.os.hmny.io/', 'https://api.s3.os.hmny.io/']
addr = 'one16xh2u9r4677egx4x3s0u966ave90l37hh7wq72'
res = []
for i in range(len(endpoint)):
    txs = getNormalTransaction(i, addr)['transactions']
    if txs != None:
        res.extend(txs)
df = pd.DataFrame.from_dict(res, orient='columns')
df['timestamp'] = df['timestamp'].apply(lambda c: datetime.datetime.fromtimestamp(c))
df['value'] = df['value'].apply(lambda c: int(c/1e18))
maggie = df[['timestamp','from','to','value']]
maggie.to_csv('./csv/maggie_transaction.csv')

