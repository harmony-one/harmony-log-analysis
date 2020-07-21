# HRC20 Holder Tracker
This project provides the backend support for [HRC20 holder tracker website](https://harmony-hrc-holder.firebaseapp.com/#/). Check frontend [here](https://github.com/ivorytowerdds/hrc20-hodler). It collects all the HRC20 wallets' address. The data is stored on [Firebase](https://console.firebase.google.com/project/harmony-explorer-mainnet/database/harmony-explorer-mainnet/data/HRC-holder). 

## Requirements
- Install packages
```
python3 -m pip install -r requirements.txt
```
- Connect to Firebase
	- [Create a Firebase project](https://console.firebase.google.com/u/0/)
	- [Add the Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup#add-sdk)
	- [Generate a private key file for your service account and initialize the SDK](https://firebase.google.com/docs/admin/setup#initialize-sdk)


## Run on a service to get holders
- Create a bash file: `vim get_holder.sh`
```
/home/ubuntu/anaconda3/bin/python3 /home/ubuntu/jupyter/harmony-log-analysis/projects/HRC_holder/HRC_20_holder.py --endpoints [ENDPOINTS] --address [ADDRES] --name [NAME]
```
- Create a service file: `sudo vim /etc/systemd/system/hrc20.service`
```
[Unit]
Description=HRC20 daemon
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=ubuntu
WorkingDirectory=/home/ubuntu/jupyter/harmony-log-analysis/projects/HRC_holder
ExecStart=/bin/bash /home/ubuntu/jupyter/harmony-log-analysis/projects/HRC_holder/get_holder.sh

[Install]
WantedBy=multi-user.target
```
- Start the service: run `sudo systemctl start hrc20`
- Automatically get it to start on boot: run `sudo systemctl enable hrc20`

## Use cronjob to get balance
- edit crontab: `crontab -e`, 
- run a cronjob every 5 minutes: `*/5 * * * * cd /home/ubuntu/jupyter/harmony-log-analysis/projects/HRC_holder && /usr/bin/node getBalance.js`

## Outputs
- logs folder: `/logs`
- data stored on [firebase](https://console.firebase.google.com/project/harmony-explorer-mainnet/database/harmony-explorer-mainnet/data/HRC-holder) 
    - query HRC20 smart contract address API: 
    ```
    curl https://harmony-explorer-mainnet.firebaseio.com/HRC-holder/address.json
    ```
    - query HRC20 smart contract name API:
    ```
    curl https://harmony-explorer-mainnet.firebaseio.com/HRC-holder/address.json
    ```
    - query HRC20 smart contract total transaction count API:
    ```
    curl https://harmony-explorer-mainnet.firebaseio.com/HRC-holder/transactions.json
    ```
    - query a specific smart contract holder API:
    ```
    curl https://harmony-explorer-mainnet.firebaseio.com/HRC-holder/[ADDRESS].json
    ```
- backup data: `/address`






