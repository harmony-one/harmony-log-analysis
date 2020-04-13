# Economic Test
Test Harmony's economic logic, including election, median, reward, consensus, delegate, undelegate, staking, slashing

## Requirements
`python3 -pip install requests`

## Commands
Run command: 
To run all test: `python3 economic-test.py --all`

To run a single test: `python3 economic-test.py --single_test [E1_test]`

To run a group of test: `python3 economic-test.py --groups [election,reward,...]` use comma to seperate different groups, no space after comma. Available options: `election, median, reward, consensus, undelegate, staking`.

To run the test when no external validators: `python3 economic-test.py --no_external`.

## Output
`./logs/*` 
