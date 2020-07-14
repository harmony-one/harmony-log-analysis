# Harmonauts Transaction History Backend
Support transaction history for harmonauts.

## Requirements
- Install packages
```
python3 -m pip install -r requirements.txt
```
- Connect to Firebase
	- [Create a Firebase project](https://console.firebase.google.com/u/0/)
	- [Add the Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup#add-sdk)
	- [Generate a private key file for your service account and initialize the SDK](https://firebase.google.com/docs/admin/setup#initialize-sdk)
    
## Commands
- Create a bash file: `vim get_punk.sh`	
```
/home/ubuntu/anaconda3/bin/python3 /home/ubuntu/jupyter/harmony-log-analysis/projects/harmonauts_dapp/get_punk_txs_history.py --endpoints [ENDPOINT] --address [ADDRESS]
```
- Create a service file: `sudo vim /etc/systemd/system/get-punk.service`
```
[Unit]
Description=get punk daemon
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=ubuntu
WorkingDirectory=/home/ubuntu/jupyter/harmony-log-analysis/projects/harmonauts_dapp
ExecStart=/bin/bash /home/ubuntu/jupyter/harmony-log-analysis/projects/harmonauts_dapp/get_punk.sh

[Install]
WantedBy=multi-user.target
```
- Start the service: run `systemctl start get-punk`
- Automatically get it to start on boot: run `systemctl enable get-punk`

## Outputs
- logs folder: `/logs`
- data stored on [firebase](https://console.firebase.google.com/u/0/project/harmony-explorer-mainnet/database/harmony-explorer-mainnet/data/harmony-punk), run API: `curl https://harmony-explorer-mainnet.firebaseio.com/harmony-punk.json`
- backup data: `/address`

## Decode Transaction History
see `punk_explore.ipynb`
