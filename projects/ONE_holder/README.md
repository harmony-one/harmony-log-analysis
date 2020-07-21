# ONE Holder Tracker
This project provides the backend support for [ONE holder tracker website](https://balance.harmony.one/#/). Check frontend [here](https://github.com/harmony-one/simple-list). It collects all the ONE address. The data is stored on [Firebase](https://console.firebase.google.com/project/harmony-explorer-mainnet/database/harmony-explorer-mainnet/data/one-holder). 

## Requirements
- Install packages
```
python3 -m pip install -r requirements.txt
```
- Connect to Firebase
	- [Create a Firebase project](https://console.firebase.google.com/u/0/)
	- [Add the Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup#add-sdk)
	- [Generate a private key file for your service account and initialize the SDK](https://firebase.google.com/docs/admin/setup#initialize-sdk)
This project provides the backend support for [ONE holder tracker website](https://balance.harmony.one/#/). Check frontend [here](https://github.com/harmony-one/simple-list). It collects all the ONE address who have txs history in mainnet history, as well as foundational nodes, and tracks the balance and txs count for each address. The data is stored on Firebase. To connect to firebase, you need to set up Admin SDK by following the [instruction](https://firebase.google.com/docs/database/admin/start#python).

## Address Collection using service
- Create a bash file: `vim getAddress.sh`
```
/home/ubuntu/anaconda3/bin/python3 /home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/getAddress.py --endpoints [ENDPOINTS] --network [MAINNET]
```
- Create a service file: `sudo vim /etc/systemd/system/get-address.service`
```
[Unit]
Description=get address daemon
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=ubuntu
WorkingDirectory=/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder
ExecStart=/bin/bash /home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/getAddress.sh

[Install]
WantedBy=multi-user.target
```
- Start the service: run `sudo systemctl start get-address`
- Automatically get it to start on boot: run `sudo systemctl enable get-address`


## Info Collection using service
- Create a bash file: `vim one-holder.sh`
```
/home/ubuntu/anaconda3/bin/python3 /home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/ONE_holder_tracker.py --endpoints [ENDPOINTS] --network [MAINNET]
```
- Create a service file: `sudo vim /etc/systemd/system/one-holder.service`
```
[Unit]
Description=ONE holder daemon
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=ubuntu
WorkingDirectory=/home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder
ExecStart=/bin/bash /home/ubuntu/jupyter/harmony-log-analysis/projects/ONE_holder/one_holder.sh

[Install]
WantedBy=multi-user.target
```
- Start the service: run `sudo systemctl start one-holder`
- Automatically get it to start on boot: run `sudo systemctl enable one-holder`


