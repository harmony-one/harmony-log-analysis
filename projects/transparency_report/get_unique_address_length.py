import os
from os import path
import datetime
import pickle
import json
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from collections import defaultdict


if __name__ == "__main__":
    base = path.dirname(path.realpath(__file__))
    data = path.abspath(path.join(base, 'data'))
    json_dir = "/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/credential"
    
    cred = credentials.Certificate(path.join(json_dir, "harmony-explorer-mainnet-firebase-adminsdk.json"))
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {'databaseURL': "https://harmony-explorer-mainnet.firebaseio.com"})  
    ref = db.reference('total-address-length')
    one_ref = ref.child('native-one')
    
    if not path.exists(data):
        try:
            os.mkdir(data)
        except:
            print("Could not make data directory")
            exit(1)

    address_file = path.join(data,'address_count.pkl')
    if path.exists(address_file):
        with open(address_file, 'rb') as f:
             address_count = pickle.load(f)
    else: 
        address_count = defaultdict(int)
    
    res = requests.get("https://harmony-explorer-mainnet.firebaseio.com/one-holder/length.json")
    length = json.loads(res.content)
    date = (datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y_%m_%d")
#     date = datetime.date.today().strftime("%Y_%m_%d")
    address_count[date] = length
    one_ref.child(date).set(length)
    
    with open(address_file, 'wb') as f:
        pickle.dump(address_count, f)
    print(f"{date} total # of one-holder address : {length}")