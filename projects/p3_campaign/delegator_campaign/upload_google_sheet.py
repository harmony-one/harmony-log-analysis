#!/usr/bin/env python
# coding: utf-8

import gspread
import pandas as pd

df = pd.read_csv("../csv/delegator.csv", index_col=0)
gc = gspread.service_account('/home/ubuntu/jupyter/harmony-log-analysis/projects/staking_dashboard/credential/jsonFileFromGoogle.json')
sh = gc.open("harmony-ostn-tracker")
worksheet = sh.worksheet("delegator")
worksheet.update([df.columns.values.tolist()] + df.values.tolist())

filter_df = pd.read_csv("csv/filter_delegator.csv", index_col=0)
sh = gc.open("harmony-ostn-tracker")
worksheet = sh.worksheet("filter-delegator")
worksheet.update([filter_df.columns.values.tolist()] + filter_df.values.tolist())
