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
newest test: [04/20](https://github.com/harmony-one/harmony-log-analysis/blob/master/projects/economic-test/logs/report_log_20200420231025_047261.log)
- Total Tests: 24
- Successful Tests: 15
- Failed Tests: 3 ['M5_test', 'R5_test', 'R11_test']
- Test doesn't meet requirements, need more tests: 3 ['E2_test', 'U1_test', 'U2_test']
- Need to manual check: 2 ['R14_test', 'S1_test']
- Not applicable for tests: 1 ['R8_test']
