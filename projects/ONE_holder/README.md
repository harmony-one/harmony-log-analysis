# ONE Holder Tracker
This project provides the backend support for [ONE holder tracker website](https://harmony-explorer-75c6d.web.app/#/). It keeps tracking all the ONE address who have txs history in mainnet history, as well foundational nodes, and tracks the balance and txs count for each address. The data is stored on Firebase. To connect to firebase, you need to set up Admin SDK by following the [instruction](https://firebase.google.com/docs/database/admin/start#python).

## Requirements
`python3 -m pip install -r requirements.txt`

## Address Collection using Tmux
Create a new tmux session using `tmux new -s address_mainnet`
Run the script: `python3 getAddress.py --endpoints [ENDPOINT] --network mainnet`

## Info Collection using a Cron job
Open list of cron jobs using `crontab -e`
Create `one_holder_track.sh` file, add the command `python3 /path/to/script/one_holder_track.py`
Currently it's running every 2 minutes, the command is `*/2 * * * * python3 /path/to/script/one_holder_track.sh` 
