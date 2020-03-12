#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import shutil
import datetime
import plotly_express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def read_data(files, path):
    data = []
    for file in files:
        with open(path + file, errors='ignore') as f:
            for line in f.readlines():
                try:
                    if not is_json(line):
                        continue
                    data.append(json.loads(line))
                except:
                    print('bad json: ', line)
    return data


# convert the data into pandas dataframe
def data_processing(data):
    df = pd.DataFrame(data)

    # convert all the keys in the staking into columns, fill nan values
    df = pd.concat([df.drop(['staking'], axis=1), df['staking'].apply(pd.Series)], axis=1)
    df.fillna(0, inplace = True)

    # drop duplicates
    df.drop_duplicates(inplace = True)

    # sort by time
    df.sort_values(by=['timestamp'], inplace = True)
    df.reset_index(drop = True, inplace = True)

    # remove some useless time
    df = df.iloc[1300:]
    df.reset_index(drop = True, inplace = True)

    # convert timestamp to datetime64[ns]
    df["timestamp"] = df["timestamp"].apply(lambda t: t.replace(" +0000 UTC",""))
    df["timestamp"] = pd.to_datetime(df['timestamp'])

    # do calculation for each shard
    shard = []
    for name, s in df.groupby("shard"):
        shard.append(s.reset_index(drop = True))

    # calculate the average time per block, transaction_per_second
    for s in shard:
        # time per block
        s["time_diff"] = (s['timestamp']-s['timestamp'].shift()).fillna(pd.Timedelta(seconds=0))
        s["block_diff"] = (s['block']-s['block'].shift()).fillna(0).astype(int)
        s["time_per_block"] = s.apply(lambda c: c["time_diff"].seconds /c["block_diff"]                                       if c["block_diff"] != 0 else np.nan, axis = 1)

        # plain transaction_per_second
        s["transaction_per_second"] = s.apply(lambda c: c["transactions"]/c["time_diff"].seconds                                               if c["time_diff"].seconds != 0 else np.nan, axis = 1)
        # staking transaction_per_second
        s["staking_transaction_per_second"] = s.apply(lambda c: c["total"]/c["time_diff"].seconds                                               if c["time_diff"].seconds != 0 else np.nan, axis = 1)
        # total transacton per second
        s["total_transaction_per_second"] = s["transaction_per_second"] + s["staking_transaction_per_second"]

        s.rename(columns={"total": "total_staking"}, inplace = True)
        s.drop(['time_diff', 'block_diff'], axis=1, inplace = True)
    return shard


log_path = "../../logs/test_logs/stress_test_02_27/"
fig_folder = "../../graphs/test_logs/stress_test_02_27/"
if os.path.exists(fig_folder):
    shutil.rmtree(fig_folder)
    os.mkdir(fig_folder)

files = os.listdir(log_path)
data = read_data(files, log_path)
shard = data_processing(data)

# get the index of blockchain changes

index = []
for s in shard:
    i = s[s['time_per_block'] < 0].index.tolist()
    i.insert(0,0)
    i.append(len(s))
    index.append(i)

state = "When DOS Enabled in Tx Pool"
df = []
for s in range(len(shard)):
    df.append(shard[s].iloc[index[s][1]+1:index[s][2]])
new = pd.concat(df)

col_options = [dict(label=x, value=x) for x in new.columns]
# dimensions = ["x", "y", "color", "facet_col", "facet_row"]
dimensions = ["x", "y", "color"]

app = dash.Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

app.layout = html.Div(
    [
        html.H1("Log Analysis and Visualization " + state),
        html.Div(
            [
                html.P([d + ":", dcc.Dropdown(id=d, options=col_options)])
                for d in dimensions
            ],
            style={"width": "25%", "float": "left"},
        ),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
    ]
)


@app.callback(Output("graph", "figure"), [Input(d, "value") for d in dimensions])
def make_figure(x, y, color):
    return px.line(
        new,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=["#00AEE9","#FFA07A","#758796"],
        hover_data = new.columns.tolist()
    )


app.run_server(debug=True)
