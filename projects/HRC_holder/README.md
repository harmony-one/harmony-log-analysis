# HRC20 Holder Tracker
This project provides the backend support for [HRC20 holder tracker website](https://harmony-hrc-holder.firebaseapp.com/#/). Check frontend [here](https://github.com/ivorytowerdds/hrc20-hodler). It collects all the ONE address who have txs history in mainnet history, as well as foundational nodes, and tracks the balance and txs count for each address. The data is stored on Firebase. To connect to firebase, you need to set up Admin SDK by following the [instruction](https://firebase.google.com/docs/database/admin/start#python).

## Requirements
`python3 -m pip install -r requirements.txt`

## Address Collection using Tmux
Create a new tmux session using `tmux new -s [NAME]`

Run the script: `python3 HRC_20_holder.py --endpoints [ENDPOINT] --network mainnet`




