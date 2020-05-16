#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import plotly.express as px 
import plotly.graph_objects as go
from IPython.core.display import display, HTML

config = {}

# read the log file
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True
 
def read_data(path):
    data = []
    with open(path, errors='ignore') as f:
        for line in f.readlines():
            try: 
                if not is_json(line):
                    continue
                data.append(json.loads(line))
            except:
                print('bad json: ', line)
    return data

# convert the data into pandas dataframe
def data_processing(data, *args):
    
    df = pd.DataFrame(data) 
    # convert timestamp to datetime64[ns] 
    df["timestamp"] = df["timestamp"].apply(lambda t: t.replace(" +0000 UTC",""))
    df["timestamp"] = pd.to_datetime(df['timestamp'])
    
    if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
        # start_time format  '2020-02-27 06:00:00'
        print("select the time window from " + args[0] + " to " + args[1])
        df = df[(df['timestamp'] > args[0]) & (df['timestamp'] < args[1])]

    if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
        print("select the block window from " + str(args[0]) + " to " + str(args[1]))
        df = df[(df['block'] > args[0]) & (df['block'] < args[1])]
        
    # convert all the keys in the staking into columns, fill nan values
    df = pd.concat([df.drop(['staking'], axis=1), df['staking'].apply(pd.Series)], axis=1)
    df.fillna(0, inplace = True)

    # drop duplicates
    df.drop_duplicates(inplace = True)

    # sort by timestamp 
    df.sort_values(by=['timestamp'], inplace = True)

    # do calculation for each shard
    shard = []
    for name, s in df.groupby("shard"):
        shard.append(s.reset_index(drop = True))
    
    # calculate the average time per block, transaction_per_second
    for s in shard:
        # time per block
        s["time_diff"] = (s['timestamp']-s['timestamp'].shift()).fillna(pd.Timedelta(seconds=0))
        s["block_diff"] = (s['block']-s['block'].shift()).fillna(0).astype(int)
        s["epoch_diff"] = (s['epoch']-s['epoch'].shift()).fillna(0).astype(int)
        
        # time per block
        s["time_per_block"] = s.apply(lambda c: c["time_diff"].seconds/c["block_diff"] if c["block_diff"] != 0 else np.nan, axis = 1)

        # plain transaction_per_second
        s["transaction_per_second"] = s.apply(lambda c: c["transactions"]/c["time_diff"].seconds                                                if c["time_diff"].seconds != 0 else np.nan, axis = 1)
        
        if "total" in s.columns:
            # staking transaction_per_second
            s["staking_transaction_per_second"] = s.apply(lambda c: c["total"]/c["time_diff"].seconds                                               if c["time_diff"].seconds != 0 else np.nan, axis = 1)
            # total transacton per second
            s["total_transaction_per_second"] = s["transaction_per_second"] + s["staking_transaction_per_second"]

            # info for staking
            s.rename(columns={"total": "total_staking"}, inplace = True)
            if "CreateValidator" in s.columns:
                # create validator per second
                s["create_validator_per_second"] = s.apply(lambda c: c["CreateValidator"]/c["time_diff"].seconds                                                        if c["time_diff"].seconds != 0 else np.nan, axis = 1)
            if "EditValidator" in s.columns:
                # edit validator per second
                s["edit_validator_per_second"] = s.apply(lambda c: c["EditValidator"]/c["time_diff"].seconds                                                        if c["time_diff"].seconds != 0 else np.nan, axis = 1)
            if "Delegate" in s.columns:
                # delegate per second
                s["delegate_per_second"] = s.apply(lambda c: c["Delegate"]/c["time_diff"].seconds                                                        if c["time_diff"].seconds != 0 else np.nan, axis = 1)
            if "Undelegate" in s.columns:
                # undelegate per second
                s["undelegate_per_second"] = s.apply(lambda c: c["Undelegate"]/c["time_diff"].seconds                                                        if c["time_diff"].seconds != 0 else np.nan, axis = 1)
            if "CollectRewards" in s.columns:
                # CollectRewards per second
                s["collect_rewards_per_second"] = s.apply(lambda c: c["CollectRewards"]/c["time_diff"].seconds                                                        if c["time_diff"].seconds != 0 else np.nan, axis = 1)
            
        s.drop(['time_diff', 'block_diff'], axis=1, inplace = True)
        s.dropna(inplace = True)
        
    return shard

# draw the graphs with x-axis time
def draw_graph_time(df, png_path, html_dir, colors):
    
    html_path = "https://harmony-one.github.io/harmony-log-analysis/" + html_dir.replace("../../docs/", "")

    print("Features vs Time")
    print("PNG saved in " + png_path)
    print("==================================")
    
    hover = df.columns.tolist()
    
    if "staking_transaction_per_second" in df.columns:
        fig = px.line(df, x="timestamp", y="staking_transaction_per_second", color='shard', color_discrete_sequence=colors,                   title = 'Staking Transaction Per Second vs Time', hover_data=hover)
        fig.update_layout(xaxis_title="utc_time")
    #     fig.show(renderer="svg",width=900, height=500)
        fig.show()
        fig.write_html(html_dir + "staking_transaction_per_second_vs_time.html")
        print("HTML saved in ")
        display_path = html_path + "staking_transaction_per_second_vs_time.html"
        display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
        fig.write_image(png_path + "staking_transaction_per_second_vs_time.png",width=900, height=500)

        fig = px.line(df, x="timestamp", y="total_transaction_per_second", color='shard', color_discrete_sequence=colors,                   title = 'Total Transaction Per Second vs Time', hover_data=hover)
        fig.update_layout(xaxis_title="utc_time")
    #     fig.show(renderer="svg",width=900, height=500)
        fig.show()
        fig.write_html(html_dir + "total_transaction_per_second_vs_time.html")
        print("HTML saved in ")
        display_path = html_path + "total_transaction_per_second_vs_time.html"
        display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
        fig.write_image(png_path + "total_transaction_per_second_vs_time.png",width=900, height=500)
    
    fig = px.line(df, x='timestamp', y='transaction_per_second', color='shard', color_discrete_sequence=colors,                   title = 'Transaction Per Second vs Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "transaction_per_second_vs_time.html")
    print("HTML saved in " )
    display_path = html_path + "transaction_per_second_vs_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + "transaction_per_second_vs_time.png",width=900, height=500)
                    
    fig = px.line(df, x="timestamp", y="time_per_block", color='shard', color_discrete_sequence=colors, title = 'Time Per Block vs Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "time_per_block_vs_time.html")
    print("HTML saved in ")
    display_path = html_path + "time_per_block_vs_time.html" 
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + "time_per_block_vs_time.png",width=900, height=500)
    
    fig = px.line(df, x="timestamp", y="size", color='shard', color_discrete_sequence=colors, title = 'Size vs Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "size_vs_time.html")
    print("HTML saved in ")
    display_path = html_path + "size_vs_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + "size_vs_time.png",width=900, height=500)
    
    fig = px.line(df, x="timestamp", y="gas", color='shard', color_discrete_sequence=colors, title = 'Gas vs Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
    fig.show()
    fig.write_html(html_dir + "gas_vs_time.html")
    print("HTML saved in ")
    display_path = html_path + "gas_vs_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    print("")
    fig.write_image(png_path + "gas_vs_time.png",width=900, height=500)

# draw the graphs with x-axis block height
def draw_graph_block(df, png_path, html_dir, colors):

    html_path = "https://harmony-one.github.io/harmony-log-analysis/" + html_dir.replace("../../docs/", "")

    print("Features vs Block Height")
    print("PNG saved in " + png_path)
    print("==================================")
    
    hover = df.columns.tolist()
    
    if "staking_transaction_per_second" in df.columns:
        fig = px.line(df, x="block", y="staking_transaction_per_second", color='shard', color_discrete_sequence=colors,                   title = 'Staking Transaction Per Second vs Block Height', hover_data=hover)
    #     fig.show(renderer="svg",width=900, height=500)
        fig.show()
        fig.write_html(html_dir + "staking_transaction_per_second_vs_block_height.html")
        print("HTML saved in ")
        display_path = html_path + "staking_transaction_per_second_vs_block_height.html"
        display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
        fig.write_image(png_path + "staking_transaction_per_second_vs_block_height.png",width=900, height=500)

        fig = px.line(df, x="block", y="total_transaction_per_second", color='shard', color_discrete_sequence=colors,                   title = 'Total Transaction Per Second vs Block Height', hover_data=hover)
    #     fig.show(renderer="svg",width=900, height=500)
        fig.show()
        fig.write_html(html_dir + "total_transaction_per_second_vs_block_height.html")
        print("HTML saved in ")
        display_path = html_path + "total_transaction_per_second_vs_time.html"
        display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
        fig.write_image(png_path + "total_transaction_per_second_vs_block_height.png",width=900, height=500)


    fig = px.line(df, x='block', y='transaction_per_second', color='shard', color_discrete_sequence=colors,                   title = 'Transaction Per Second vs Block Height', hover_data=hover)
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "transaction_per_second_vs_block_height.html")
    print("HTML saved in " )
    display_path = html_path + "transaction_per_second_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + "transaction_per_second_vs_block_height.png",width=900, height=500)
    
    fig = px.line(df, x="block", y="time_per_block", color='shard', color_discrete_sequence=colors, title = 'Time Per Block vs Block Height', hover_data=hover)
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "time_per_block_vs_block_height.html")
    print("HTML saved in " )
    display_path = html_path + "time_per_block_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + "time_per_block_vs_block_height.png",width=900, height=500)
    
    fig = px.line(df, x="block", y="size", color='shard', color_discrete_sequence=colors, title = 'Size vs Block Height', hover_data=hover)
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "size_vs_block_height.html")
    print("HTML saved in ")
    display_path = html_path + "size_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + "size_vs_block_height.png",width=900, height=500)
    
    fig = px.line(df, x="block", y="gas", color='shard', color_discrete_sequence=colors, title = 'Gas vs Block', hover_data=hover)
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + "gas_vs_block_height.html")
    print("HTML saved in ")
    display_path = html_path + "gas_vs_block_height.html"
    display(HTML("<a href='" + display_path  + "' target='_blank'>" + display_path + "</a>"))
    print("")
    fig.write_image(png_path + "gas_vs_block_height.png",width=900, height=500)
    
# draw the graphs with x-axis utc time for each shard
def draw_graph_time_per_shard(df, png_path, html_dir, idx, epo_idx):
    
    html_path = "https://harmony-one.github.io/harmony-log-analysis/" + html_dir.replace("../../docs/", "")

    print("Features vs UTC Time Graphs for shard " + str(idx))
    print("PNG saved in " + png_path)
    print("==================================")
    
    shard_idx = "shard_"+str(idx)
    colors = ["#00AEE9"]
    hover = df.columns.tolist()
    
    if "staking_transaction_per_second" in df.columns:
        # staking only happens in shard 0
        if idx == 0:
            fig = px.line(df, x="timestamp", y="staking_transaction_per_second", color='shard', color_discrete_sequence=colors,                  title = shard_idx + ' Staking Transaction Per Second vs UTC Time', hover_data=hover)
            fig.update_layout(xaxis_title="utc_time")
            for i in epo_idx:
                fig.add_shape(type="line", x0=df.iloc[i]["timestamp"], y0=0,x1=df.iloc[i]["timestamp"],y1=1,
                        line=dict(
                        width=1,
                        dash="dot",
                    ))
            fig.update_shapes(dict(xref='x', yref='paper'))
    #         fig.show(renderer="svg",width=900, height=500)
            fig.show()
            fig.write_html(html_dir + shard_idx + "_staking_transaction_per_second_vs_utc_time.html")
            print("HTML saved in ")
            display_path = html_path + shard_idx + "_staking_transaction_per_second_vs_utc_time.html"
            display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
            fig.write_image(png_path + shard_idx + "_staking_transaction_per_second_vs_utc_time.png",width=900, height=500)

            fig = px.line(df, x="timestamp", y="total_transaction_per_second", color='shard', color_discrete_sequence=colors,                      title = shard_idx + ' Total Transaction Per Second vs UTC Time', hover_data=hover)
            fig.update_layout(xaxis_title="utc_time")
            for i in epo_idx:
                fig.add_shape(type="line", x0=df.iloc[i]["timestamp"], y0=0,x1=df.iloc[i]["timestamp"],y1=1,
                        line=dict(
                        width=1,
                        dash="dot",
                    ))
            fig.update_shapes(dict(xref='x', yref='paper'))
    #         fig.show(renderer="svg",width=900, height=500)
            fig.show()
            fig.write_html(html_dir + shard_idx + "_total_transaction_per_second_vs_utc_time.html")
            print("HTML saved in ")
            display_path = html_path + shard_idx + "_total_transaction_per_second_vs_utc_time.html"
            display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
            fig.write_image(png_path + shard_idx + "_total_transaction_per_second_vs_utc_time.png",width=900, height=500)

    fig = px.line(df, x='timestamp', y='transaction_per_second', color='shard', color_discrete_sequence=colors,               title = shard_idx + ' Transaction Per Second vs UTC Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["timestamp"], y0=0,x1=df.iloc[i]["timestamp"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_transaction_per_second_vs_utc_time.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_transaction_per_second_vs_utc_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + shard_idx + "_transaction_per_second_vs_utc_time.png",width=900, height=500)
    
    fig = px.line(df, x="timestamp", y="time_per_block", color='shard', color_discrete_sequence=colors, title = shard_idx + ' Time Per Block vs UTC Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["timestamp"], y0=0,x1=df.iloc[i]["timestamp"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_time_per_block_vs_utc_time.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_time_per_block_vs_utc_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + shard_idx + "_time_per_block_vs_utc_time.png",width=900, height=500)
    
    fig = px.line(df, x="timestamp", y="size", color='shard', color_discrete_sequence=colors, title = shard_idx + ' Size vs UTC Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["timestamp"], y0=0,x1=df.iloc[i]["timestamp"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_size_vs_utc_time.html")
    print("HTML saved in " )
    display_path = html_path + shard_idx + "_size_vs_utc_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + shard_idx + "_size_vs_utc_time.png",width=900, height=500)


    fig = px.line(df, x="timestamp", y="gas", color='shard', color_discrete_sequence=colors, title = shard_idx + ' Gas vs UTC Time', hover_data=hover)
    fig.update_layout(xaxis_title="utc_time")
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["timestamp"], y0=0,x1=df.iloc[i]["timestamp"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_gas_vs_utc_time.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_gas_vs_utc_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    print("")
    fig.write_image(png_path + shard_idx + "_gas_vs_utc_time.png",width=900, height=500)

# draw the graphs with x-axis block height for each shard
def draw_graph_block_per_shard(df, png_path, html_dir, idx, epo_idx):
    
    html_path = "https://harmony-one.github.io/harmony-log-analysis/" + html_dir.replace("../../docs/", "")

    print("Features vs Block Height Graphs for shard " + str(idx))
    print("PNG saved in " + png_path)
    print("==================================")
    
    shard_idx = "shard_"+str(idx)
    colors = ["#00AEE9"]
    hover = df.columns.tolist()
    
    if "staking_transaction_per_second" in df.columns:
        # staking only happens in shard_0
        if idx == 0:
            fig = px.line(df, x="block", y="staking_transaction_per_second", color='shard', color_discrete_sequence=colors,                      title = shard_idx + ' Staking Transaction Per Second vs Time', hover_data=hover)
            for i in epo_idx:
                fig.add_shape(type="line", x0=df.iloc[i]["block"], y0=0,x1=df.iloc[i]["block"],y1=1,
                        line=dict(
                        width=1,
                        dash="dot",
                    ))
            fig.update_shapes(dict(xref='x', yref='paper'))
    #         fig.show(renderer="svg",width=900, height=500)
            fig.show()
            fig.write_html(html_dir + shard_idx + "_staking_transaction_per_second_vs_block_height.html")
            print("HTML saved in " )
            display_path = html_path + shard_idx + "_staking_transaction_per_second_vs_block_height.html"
            display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
            fig.write_image(png_path + shard_idx + "_staking_transaction_per_second_vs_block_height.png")

            fig = px.line(df, x="block", y="total_transaction_per_second", color='shard', color_discrete_sequence=colors,                      title = shard_idx + ' Total Transaction Per Second vs Time', hover_data=hover)
            for i in epo_idx:
                fig.add_shape(type="line", x0=df.iloc[i]["block"], y0=0,x1=df.iloc[i]["block"],y1=1,
                        line=dict(
                        width=1,
                        dash="dot",
                    ))
            fig.update_shapes(dict(xref='x', yref='paper'))
    #         fig.show(renderer="svg",width=900, height=500)
            fig.show()
            fig.write_html(html_dir + shard_idx + "_total_transaction_per_second_vs_block_height.html")
            print("HTML saved in ")
            display_path = html_path + shard_idx + "_total_transaction_per_second_vs_block_height.html"
            display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
            fig.write_image(png_path + shard_idx + "_total_transaction_per_second_vs_block_height.png")
    
    fig = px.line(df, x='block', y='transaction_per_second', color='shard', color_discrete_sequence=colors, title = shard_idx + ' Transaction Per Second vs Block Height', hover_data=hover)
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["block"], y0=0,x1=df.iloc[i]["block"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_transaction_per_second_vs_block_height.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_transaction_per_second_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + shard_idx + "_transaction_per_second_vs_block_height.png")

    fig = px.line(df, x="block", y="time_per_block", color='shard', color_discrete_sequence=colors, title = shard_idx + ' Time Per Block vs Time', hover_data=hover)
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["block"], y0=0,x1=df.iloc[i]["block"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_time_per_block_vs_block_height.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_time_per_block_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + shard_idx + "_time_per_block_vs_block_height.png")


    fig = px.line(df, x="block", y="size", color='shard', color_discrete_sequence=colors, title = shard_idx + ' Size vs Time', hover_data=hover)
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["block"], y0=0,x1=df.iloc[i]["block"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_size_vs_block_height.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_size_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    fig.write_image(png_path + shard_idx + "_size_vs_block_height.png")


    fig = px.line(df, x="block", y="gas", color='shard', color_discrete_sequence=colors, title = shard_idx + ' Gas vs Time', hover_data=hover)
    for i in epo_idx:
        fig.add_shape(type="line", x0=df.iloc[i]["block"], y0=0,x1=df.iloc[i]["block"],y1=1,
                line=dict(
                width=1,
                dash="dot",
            ))
    fig.update_shapes(dict(xref='x', yref='paper'))
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_gas_vs_block_height.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_gas_vs_block_height.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    print("")
    fig.write_image(png_path + shard_idx + "_gas_vs_block_height.png")
    

# draw the graphs with x-axis block height for each shard
def draw_staking_graph_time_per_shard(df, png_path, html_dir, idx):
    
    html_path = "https://harmony-one.github.io/harmony-log-analysis/" + html_dir.replace("../../docs/", "")

    print("Staking Features vs UTC Time Graphs for shard " + str(idx))
    print("PNG saved in " + png_path)
    print("==================================")    
    
    shard_idx = "shard_"+str(idx)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x= df["timestamp"],
        y= df["staking_transaction_per_second"],
        mode='lines',
        name='staking_transaction_per_second',
        line_color= "#F5B7B1"
    ))

    if "create_validator_per_second" in df.columns:              
        fig.add_trace(go.Scatter(
            x= df["timestamp"],
            y= df["create_validator_per_second"],
            mode = "lines",
            line_color = "#85C1E9",
            name='create_validator_per_second'   
        ))
    
    if "edit_validator_per_second" in df.columns:
        fig.add_trace(go.Scatter(
            x= df["timestamp"],
            y= df["edit_validator_per_second"],
            mode = "lines",
            line_color = "#D7BDE2",
            name='edit_validator_per_second'
        ))

    if "delegate_per_second" in df.columns:        
        fig.add_trace(go.Scatter(
            x= df["timestamp"],
            y= df["delegate_per_second"],
            mode = "lines",
            line_color = "#66CDAA",
            name='delegate_per_second'
        ))
    
    if "undelegate_per_second" in df.columns:
        fig.add_trace(go.Scatter(
            x= df["timestamp"],
            y= df["undelegate_per_second"],
            mode = "lines",
            line_color = "#F4D03F",
            name='undelegate_per_second'
        ))
    
    if "collect_rewards_per_second" in df.columns:
        fig.add_trace(go.Scatter(
            x= df["timestamp"],
            y= df["collect_rewards_per_second"],
            mode='lines',
            name='collect_rewards_per_second',
            line_color= "#AEB6BF"
        ))
    
    fig.update_layout(title='Staking Features vs UTC Time for Shard ' + str(idx), xaxis_title='UTC Time',                   yaxis_title='Different Transaction Per Second', legend_orientation="h", legend=dict(x=0, y=-0.25))

#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_staking_info_vs_time.html")
    print("HTML saved in ")
    display_path = html_path + shard_idx + "_staking_info_vs_time.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    print("")
    fig.write_image(png_path + shard_idx + "_staking_info_vs_time.png",width=900, height=500)

# draw the graphs with x-axis block height for each shard
def draw_staking_graph_block_per_shard(df, png_path, html_dir, idx):

    html_path = "https://harmony-one.github.io/harmony-log-analysis/" + html_dir.replace("../../docs/", "")

    print("Staking Features vs Block Height Graphs for shard " + str(idx))
    print("PNG saved in " + png_path)
    print("==================================")  
    
    shard_idx = "shard_"+str(idx)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x= df["block"],
        y= df["staking_transaction_per_second"],
        mode='lines',
        name='staking_transaction_per_second',
        line_color= "#F5B7B1"
    ))
    
    if "create_validator_per_second" in df.columns:  
        fig.add_trace(go.Scatter(
            x= df["block"],
            y= df["create_validator_per_second"],
            mode = "lines",
            marker_color = "#85C1E9",
            name='create_validator_per_second'   
        ))
    
    if "edit_validator_per_second" in df.columns:
        fig.add_trace(go.Scatter(
            x= df["block"],
            y= df["edit_validator_per_second"],
            mode = "lines",
            marker_color = "#D7BDE2",
            name='edit_validator_per_second'
        ))

    if "delegate_per_second" in df.columns:         
        fig.add_trace(go.Scatter(
            x= df["block"],
            y= df["delegate_per_second"],
            mode = "lines",
            marker_color = "#66CDAA",
            name='delegate_per_second'
        ))
    
    if "undelegate_per_second" in df.columns:
        fig.add_trace(go.Scatter(
            x= df["block"],
            y= df["undelegate_per_second"],
            mode = "lines",
            marker_color = "#F4D03F",
            name='undelegate_per_second'
        ))
    
    if "collect_rewards_per_second" in df.columns:
        fig.add_trace(go.Scatter(
            x= df["block"],
            y= df["collect_rewards_per_second"],
            mode='lines',
            name='collect_rewards_per_second',
            marker_color= "#AEB6BF"
        ))
    
    fig.update_layout(title='Staking Features vs Block Height for Shard ' + str(idx), xaxis_title='Block',                   yaxis_title='Different Transaction Per Second', legend_orientation="h", legend=dict(x=0, y=-0.2))
    
#     fig.show(renderer="svg",width=900, height=500)
    fig.show()
    fig.write_html(html_dir + shard_idx + "_staking_info_vs_block.html")
    print("HTML saved in " )
    display_path = html_path + shard_idx + "_staking_info_vs_block.html"
    display(HTML("<a href='" + display_path + "' target='_blank'>" + display_path + "</a>"))
    print("")
    fig.write_image(png_path + shard_idx + "_staking_info_vs_block.png",width=900, height=500)

# print the statistics summary 
def print_statistic_summary(df, columns, name):
    
    print("Statistics summary for shard " + str(name))
    print("==================================")
    summary = df[columns].describe()
    print("Total data points: " + str(summary.iloc[0][0].astype(int)))
    print(summary.iloc[1:])
    print("")

def set_config(input_config):
    assert isinstance(input_config, dict)
    config.clear()
    config.update(input_config)
    
def visualization(new, fig_path, html_dir, config):
    stat_columns = ["size", "gas", "transaction_per_second", "time_per_block"]  
    colors = ["#00AEE9", "#FFA07A", "#758796", "#66CDAA"]
    for name, group in new.dropna().groupby("shard"):
        # statistics summary for each shard
        group.reset_index(inplace = True, drop = True)
        if not config['ignore_printing_statistics_summary']:
            print_statistic_summary(group, stat_columns, name)

        epo_idx = group[group['epoch_diff'] > 0].index.tolist()
        # draw fearures vs time for each shard
        if not config['ignore_drawing_features_vs_time_per_shard']:
            draw_graph_time_per_shard(group, fig_path, html_dir, name, epo_idx)

        # draw fearures vs block for each shard
        if not config['ignore_drawing_features_vs_block_per_shard']:
            draw_graph_block_per_shard(group, fig_path, html_dir, name, epo_idx)

        # draw staking fearures vs time for each shard
        if not config['ignore_drawing_staking_features_vs_time_per_shard'] and name == 0:
            draw_staking_graph_time_per_shard(group, fig_path, html_dir, name)

        # draw staking fearures vs block for each shard   
        if not config['ignore_drawing_staking_features_vs_block_per_shard'] and name == 0:
            draw_staking_graph_block_per_shard(group, fig_path,html_dir, name)

    # draw fearures vs time 
    if not config['ignore_drawing_features_vs_time']:
        draw_graph_time(new, fig_path, html_dir, colors)
    # draw fearures vs block 
    if not config['ignore_drawing_features_vs_block']:
        draw_graph_block(new, fig_path, html_dir, colors)
