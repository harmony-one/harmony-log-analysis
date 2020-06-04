import pickle
import pandas as pd
from os import path
import gspread

base = path.dirname(path.realpath(__file__))
pkl_dir = path.abspath(path.join(base, 'pickle'))
csv_dir = path.abspath(path.join(base, 'csv'))
addr_dir = path.abspath(path.join(base, 'address'))

def getSigningPerc(sign, count):
    perc = dict()
    shard_dict = dict()
    for shard, value in count.items():
        for k, v in value.items():
            if k in sign[shard]:
                perc[k] = sign[shard][k]/v
                shard_dict[k] = shard
            else:
                perc[k] = 0
                shard_dict[k] = shard
    return perc, shard_dict

sign_file = path.join(pkl_dir,'signer_count_mainnet.pickle')
with open(sign_file, 'rb') as f:
    sign = pickle.load(f)


count_file = path.join(pkl_dir,'committee_count_mainnet.pkl')
with open(count_file, 'rb') as f:
    count = pickle.load(f)

perc, shard_dict = getSigningPerc(sign, count)

perc_df = pd.DataFrame(perc.items(), columns=['address', 'signing-percentage'])
shard_df = pd.DataFrame(shard_dict.items(), columns=['address', 'shard'])
df = perc_df.join(shard_df.set_index('address'), on = 'address')

filename = path.join(addr_dir, 'fn_addresses.csv')
fn_addr = pd.read_csv(filename, header = None, names = ['address', 'shard'])
address = fn_addr['address'].tolist()
df['is-FN'] = df['address'].apply(lambda c: True if c in address else False)

df.to_csv(path.join(csv_dir, "signing_percentage.csv"))
print("Successfully saving signing percentage to csv")

json_file = path.join(base, 'credential/jsonFileFromGoogle.json')
gc = gspread.service_account(json_file)
sh = gc.open("harmony-mainnet-tracker")
worksheet = sh.worksheet("signing-percentage")
worksheet.update([df.columns.values.tolist()] + df.values.tolist())
print("Successfully uploading signing percentage to google sheet")