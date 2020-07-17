const { Harmony, HarmonyExtension } = require('@harmony-js/core');
const { ChainID, ChainType } = require('@harmony-js/utils');
const contractConfig = require('./config.js');


// get a contract instance

var account = '0x217435D2D6A1F42CD0e93e23b61C20A426D898A7';

async function getBUSDbalance(account) {

  let hmy = new Harmony(contractConfig.url, {
    chainType: ChainType.Harmony,
    chainId: ChainID.HmyMainnet,
  })

  const contract = hmy.contracts.createContract(contractConfig.abi, contractConfig.address)
  const balance = contract.methods.balanceOf(account)
  console.log("contract", contract);
  process.exit(0);
}


getBUSDbalance(account);

                             


