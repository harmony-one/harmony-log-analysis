#!/usr/bin/env python
# coding: utf-8
import logging
import argparse
from utils import *
import test_case
from test_case import *
        
def run_test(curr_test):
    global success, fail, more, manual, error, no, count, fail_lst, more_lst, check_lst, error_lst, no_lst, single
    test_name = curr_test.__name__
    test_case.logger.info(f"\n{'=' * 15} Starting {test_name} {'=' * 15}\n")                        
    res, curr_test = curr_test(single) 
    if res == True:
        success += 1
    elif res == False:
        fail += 1
        fail_lst.append(test_name)
    elif res == 'Need More Tests':
        more += 1
        more_lst.append(test_name)
    elif res == 'Need Manually Check':
        manual += 1
        check_lst.append(test_name)
    elif res == "Not Applicable":
        no += 1
        no_lst.append(test_name)  
    else:
        error += 1
        error_lst.append(test_name)
    count += 1
    return curr_test
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action = 'store_true', help = 'Run all the tests')
    parser.add_argument('--single_test', help = 'Run the single test, example: E1_test')
    parser.add_argument('--groups', help = 'Type of test to run, seperated by commas, options: election, median, reward, consensus, undelegate, staking')
    parser.add_argument('--no_external', action = 'store_true', help = 'Run the test when there is no external validators')

    success, fail, more, manual, error, no, count = 0, 0, 0, 0, 0, 0, 0
    fail_lst, more_lst, check_lst, error_lst, no_lst = [], [], [], [], []
    single = False
    args = parser.parse_args()
    group = []
    
    if not args.all and not args.single_test and not args.groups and not args.no_external:
        print('Keyword to define the test scope is required, e.g. --all, --single_test E1_test, --groups election, --no_external.')
        exit(1)
        
    if args.all:
        group = ['election', 'median', 'reward', 'consensus', 'undelegate', 'staking']
            
    if args.groups:
        group = [x.strip() for x in args.groups.strip().split(',')]
        
    if args.no_external:
        no_external_test = M4_test
        while no_external_test:
            no_external_test = run_test(no_external_test)
    
    if args.single_test:
        single = True
        run_test(getattr(test_case, args.single_test))
    
    for i in group:
        if i == 'election':
            curr_test = E1_test
        elif i == 'median':
            curr_test = M2_test
        elif i == 'reward':
            curr_test = R1_test
        elif i == 'consensus':
            curr_test = CN1_test
        elif i == 'delegate':
            curr_test = None
            print("currently no test for delegation")
        elif i == 'undelegate':
            curr_test = U1_test
        elif i == 'staking':
            curr_test = S1_test
        elif i == 'slashing':
            curr_test = None
            print("currently no test for slashing")
        else:
            print("Key word is not correct, options: election, median, reward, consensus, undelegate, staking")
            exit(1)
        while curr_test:
            curr_test = run_test(curr_test)
   
    test_case.logger.info(f"\n{'=' * 25} Test Results {'=' * 25}\n")
    test_case.logger.info(f"Total Tests: {count}")
    test_case.logger.info(f"Successful Tests: {success}")
    test_case.logger.info(f"Failed Tests: {fail}")
    if fail_lst:
        test_case.logger.info(f"{fail_lst}")
    test_case.logger.info(f"Test doesn't meet requirements, need more tests: {more}")
    if more_lst:
        test_case.logger.info(f"{more_lst}")
    test_case.logger.info(f"Need to manual check: {manual}")
    if check_lst:
        test_case.logger.info(f"{check_lst}")
    test_case.logger.info(f"Not applicable for tests: {no}")
    if no_lst:
        test_case.logger.info(f"{no_lst}")
    test_case.logger.info(f"Error tests: {error}")
    if error_lst:
        test_case.logger.info(f"{error_lst}")
       

