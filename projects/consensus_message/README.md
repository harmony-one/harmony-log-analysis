# Consensus Messsage Analysis
This project provides the analysis on consensus message.

## Retry analysis
If due to some reasons, the validator doesn't receive the consensus messaage from the leader, the leader will retry sending message. Currently our network allows min(6 retry, timeout), if the leader still fails to send message, then it will cause view change. In this project, we want to know the retry percentage in our networrk. We would like to expect less than 1% retry in mainnet, which is a good sign for the network. In the project, we also include the analysis about newview retry, crosslink retry for different networks.
- [ostn retry](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/OSTN_02_28-03_04_retry.ipynb)
- [stn retry](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/stn_03_04_retry.ipynb)
- [mainnet retry](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/mainnet_03_09_retry.ipynb)
- [stn crosslink retry](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/stn_03_04_crosslink_retry.ipynb)

## Message loss analysis
Each validator should receive announce, prepared, committed message sent from the leader consecutively. ([reference](https://github.com/harmony-one/harmony/blob/614f528f2ceebd1d4e340a82e33f77f9624541b3/consensus/README.md) But currently we noticed some of the consensus message is missing. This project is to explore what message is missing and how much we are missing and try to find the pattern of message missing.
- [ostn](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/message_loss_ostn.ipynb): Date: 04/14, Validator Number: 9, Result: All checked validators only received prepared message.
- [mainnet](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/message_loss_mainnet.ipynb): Date: 04/10 - 04/19, Validator Number: 10, Result: on 4/14 and 4/19, we both have one commited and one announce message missing for all 10 validators. 
Based on the result, we can see the issue should be more on the leader side since the missing issue happens on all validators level.

## ViewID check
ViewID is similar to block height, but will always be no less than block height since whenever there is a viewchange, the viewID will increaae. The viewID should be consecutive, and only increase not decrease. This project is used to check whether viewID is recorded right. 
- [ostn](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/viewID_check_ostn.ipynb)
- [mainnet](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/consensus_message/viewid_check_mainnet.ipynb)
