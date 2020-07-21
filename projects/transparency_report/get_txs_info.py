import os
from os import path
import datetime
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db
from collections import defaultdict
import requests
import json

if __name__ == "__main__":
    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'data'))
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make data directory")
            exit(1)

    txs_file = path.join(data,'txs_count.pkl')
    if path.exists(txs_file):
        with open(txs_file, 'rb') as f:
             txs_count = pickle.load(f)
    else: 
        txs_count = defaultdict(int)
    
    staking_txs_file = path.join(data,'staking_txs_count.pkl')
    if path.exists(staking_txs_file):
        with open(txs_file, 'rb') as f:
             staking_txs_count = pickle.load(f)
    else: 
        staking_txs_count = defaultdict(int)
            
    json_dir = "/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/credential"

    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})
    client = firestore.client()
    ref = db.reference('total-txs-count')
    staking_ref = db.reference('daily-stakingTxs-count')
    
    txs = 0
    for i in range(4):
        txs += client.collection(u'data').document(u'shard{}'.format(i)).get().to_dict()['txCount']
        
    staking_txs = client.collection(u'data').document(u'shard0').get().to_dict()['stakingTxCount']

    date = (datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y_%m_%d")
#     date = datetime.date.today().strftime("%Y_%m_%d")
    txs_count[date] = txs
    staking_txs_count[date] = staking_txs
    ref.child(date).set(txs)
    staking_ref.child(date).set(staking_txs)
    with open(txs_file, 'wb') as f:
        pickle.dump(txs_count, f)
    with open(staking_txs_file, 'wb') as f:
        pickle.dump(txs_count, f)

    print(f"{date} txs count: {txs}")
    print(f"{date} staking count: {staking_txs}")
