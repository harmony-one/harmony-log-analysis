

const { Harmony, HarmonyExtension } = require('@harmony-js/core');
const { ChainID, ChainType } = require('@harmony-js/utils');
const contractConfig = require('./config.js');

var admin = require("firebase-admin");

// Fetch the service account key JSON file contents
var serviceAccount = require("./credential/harmony-explorer-mainnet-firebase-adminsdk.json");

// Initialize the app with a service account, granting admin privileges
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://harmony-explorer-mainnet.firebaseio.com"
});

// As an admin, the app has access to read and write all data, regardless of Security Rules
var db = admin.database();
var ref = db.ref("HRC-holder/one10y76c0kyj6d9hmngf0859yx49l4c75d5z77zxr/");
var addrRef = ref.child("address");
var accountArray = [];
var balanceArray = [];
var balanceRef = ref.child("balance");

let hmy = new Harmony(contractConfig.url, {
    chainType: ChainType.Harmony,
    chainId: ChainID.HmyMainnet,
})

let gasConfig = {
    gasLimit: '0.005',
    gasPrice: new hmy.utils.Unit('1000000').asGwei().toWei(),
};

// get a contract instance  
const contract = hmy.contracts.createContract(contractConfig.abi, contractConfig.address);

async function getSeedBalance(accountB32, balance) {   
    for (i = 0; i < accountB32.length; i++){
        let account = hmy.crypto.fromBech32(accountB32[i])
        await contract.methods.balanceOf(account).call(gasConfig).then((data) => {
            let res = data['words'][0]
            balance.push(res/1e6);
            console.log("account", account, "balance", res/1e6);            
        })
    }
//     console.log("balance", balance);
    balanceRef.set(balance)
}

addrRef.on("value", function(snapshot) {
    accountArray = snapshot.val();
//     console.log("account ", accountArray);
    getSeedBalance(accountArray, balanceArray);    
});

