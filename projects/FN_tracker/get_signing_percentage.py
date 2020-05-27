import pickle
import pandas as pd

def getSigningPerc(sign, count):
    perc = dict()
    for k, v in count.items():
        if k in sign:
            perc[k] = sign[k]/v
        else:
            perc[k] = 0
    return perc

sign_file = path.join(pkl_dir,'sign_{}.pickle'.format(network))
with open(sign_file, 'rb') as f:
    sign = pickle.load(f)


count_file = path.join(pkl_dir,'count_{}.pickle'.format(network))
with open(count_file, 'rb') as f:
    count = pickle.load(f)

perc = getSigningPerc(sign, count)
df = pd.DataFrame(perc.items(), columns=['address', 'signing-percentage'])

df.to_csv(path.join(csv, "block_signer.csv"))
print("Successfully saving signing percentage to csv")