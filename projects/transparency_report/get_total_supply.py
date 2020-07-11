import pyhmy
from pyhmy import blockchain
import datetime
from os import path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
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

def getCirculatingSupply(shard):
    url = endpoint[shard]
    method = 'hmy_getCirculatingSupply'
    params = []
    return get_information(url, method, params)['result']

def getTotalSupply(shard):
    url = endpoint[shard]
    method = 'hmy_getTotalSupply'
    params = []
    return get_information(url, method, params)['result']

def getStakingNetworkInfo(shard):
    url = endpoint[shard]
    method = 'hmy_getStakingNetworkInfo'
    params = []
    return get_information(url, method, params)['result']

if __name__ == "__main__":
    endpoint = ['https://api.s0.t.hmny.io/', 'https://api.s1.t.hmny.io/', 'https://api.s2.t.hmny.io/', 'https://api.s3.t.hmny.io/']
    initial = float(getTotalSupply(0))
    block_reward = 28
    # when we enter into the open staking 
    shard_0 = 3375104
    shard_1 = 3286736
    shard_2 = 3326152
    shard_3 = 3313571
    
    json_dir = "/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/credential"
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})  
    
    total_block = 0
    for s in range(4):
        total_block += blockchain.get_latest_header(endpoint=endpoint[s])['blockNumber']
    total_supply = (total_block - (shard_0 + shard_1 + shard_2 + shard_3))*block_reward + initial
    
    unlocked = float(getCirculatingSupply(0))
    circulating_supply =  unlocked + (total_block - (shard_0 + shard_1 + shard_2 + shard_3))*block_reward 
    
    total_stake = getStakingNetworkInfo(0)['total-staking']/1e18
    staking_ratio = total_stake/circulating_supply
    
    date = (datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y_%m_%d")
#     date = datetime.date.today().strftime("%Y_%m_%d")
    total_ref = db.reference('total-supply')
    print(f"total_supply: {date} {total_supply}")
    total_ref.child(date).set(total_supply)
    
    circulating_ref = db.reference('circulating-supply')
    print(f"circulating_supply: {date} {circulating_supply}")
    circulating_ref.child(date).set(circulating_supply)
    
    ratio_ref = db.reference('staking-ratio')
    print(f"staking_ratio: {date} {staking_ratio}")
    ratio_ref.child(date).set(staking_ratio)
    
    
    