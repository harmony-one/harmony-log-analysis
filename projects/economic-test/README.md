# Economic Test
Test Harmony's economic logic, including election, median, reward, consensus, delegate, undelegate, staking, slashing

## Requirements
`python3 -pip install requests`

## Commands
Run command: 
To run all test: e.g. `python3 economic-test.py --all`

To run a single test: e.g. `python3 economic-test.py --single_test E1_test`

To run a group of test: e.g. `python3 economic-test.py --groups election,reward` use comma to seperate different groups, no space after comma. Available options: `election, median, reward, consensus, undelegate, staking`.

To run the test when no external validators: `python3 economic-test.py --no_external`.

## Output
`./logs/*`

## Status
newest test: 04/20 
2020-04-20 23:53:03,503: INFO: Total Tests: 24
2020-04-20 23:53:03,504: INFO: Successful Tests: 15
2020-04-20 23:53:03,504: INFO: Failed Tests: 3
2020-04-20 23:53:03,504: INFO: ['M5_test', 'R5_test', 'R11_test']
2020-04-20 23:53:03,504: INFO: Test doesn't meet requirements, need more tests: 3
2020-04-20 23:53:03,504: INFO: ['E2_test', 'U1_test', 'U2_test']
2020-04-20 23:53:03,504: INFO: Need to manual check: 2
2020-04-20 23:53:03,504: INFO: ['R14_test', 'S1_test']
2020-04-20 23:53:03,504: INFO: Not applicable for tests: 1
2020-04-20 23:53:03,504: INFO: ['R8_test']
