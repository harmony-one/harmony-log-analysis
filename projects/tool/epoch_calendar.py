#!/usr/bin/env python
# coding: utf-8

import pyhmy
from pyhmy import (
    blockchain
)
import logging
from datetime import datetime
from pytz import timezone
from os import path
import os
import json
import time

if __name__ == "__main__":
    
    base = path.dirname(path.realpath("epoch_calendar.ipynb"))
    log_dir = path.abspath(path.join(base, 'logs'))
    if not path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except:
            print("Could not make data directory")
            exit(1)
            
    logger = logging.getLogger("calendar")
    logger.setLevel(logging.INFO)
    filename = "epoch_calendar.log"
    file_handler = logging.FileHandler(path.join(log_dir, filename))
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
            
    mainnetEpochBlock1 = 344064
    blocksPerEpoch = 16384
    endpoint = 'https://api.s0.t.hmny.io/'
    staking_epoch = blockchain.get_staking_epoch(endpoint)
    curr_epoch = blockchain.get_current_epoch(endpoint)
    for i in range(staking_epoch, curr_epoch+1): 
        block_num = mainnetEpochBlock1 + blocksPerEpoch*(i-1)
        timestamp = int(blockchain.get_block_by_number(block_num, endpoint)['timestamp'],16)
        cst_time = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d_%H:%M:%S')
        pst_time = datetime.fromtimestamp(timestamp).astimezone(timezone('US/Pacific')).strftime('%Y_%m_%d_%H:%M:%S')
        t = {
            "epoch": i,
            "block": block_num,
            "cst_time": cst_time,
            "pst_time": pst_time
        }
        logger.info(json.dumps(t))
    
    
    while True:
        epoch = blockchain.get_current_epoch(endpoint)
        while epoch == curr_epoch:
            time.sleep(3600)
            epoch = blockchain.get_current_epoch(endpoint)
        block_num = mainnetEpochBlock1 + blocksPerEpoch*(epoch - 1)
        timestamp = int(blockchain.get_block_by_number(block_num, endpoint)['timestamp'],16)
        cst_time = datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d_%H:%M:%S')
        pst_time = datetime.fromtimestamp(timestamp).astimezone(timezone('US/Pacific')).strftime('%Y_%m_%d_%H:%M:%S')
        t = {
            "epoch": epoch,
            "block": block_num,
            "cst_time": cst_time,
            "pst_time": pst_time
        }
        logger.info(json.dumps(t))
        curr_epoch = epoch