from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
with open("abi_mock.json", "r") as abi_file:
    abi = json.load(abi_file)
with open("abi_mock_stake.json", "r") as abi_file:
    abi_stake = json.load(abi_file)
contract_address = "0x800eC0D65adb70f0B69B7Db052C6bd89C2406aC4"
w3 = Web3(Web3.HTTPProvider("https://sepolia-eth.w3node.com/5676fec5e57b90295400cbc24876a83258949c1cff217e0e6965bb3677557312/api"))
contract_mock_token=w3.eth.contract(address=contract_address, abi=abi)
contract_mock_stake=w3.eth.contract(address="0x7abF52a91D3D078960BAFC9912fa1bE248ef6dcf", abi=abi_stake)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
def mint_mock(private_key):
    account = w3.eth.account.from_key(private_key)
    transaction={
        "to": contract_address,
        "value": 0,
        "gas": 2000000,
        "gasPrice": w3.eth.gas_price*2 ,
        "nonce": w3.eth.get_transaction_count(account.address),
        "chainId": 11155111,
        "data": "0xc63d75b6000000000000000000000000"+account.address[2:]
    }
    estimate = w3.eth.estimate_gas(transaction)
    transaction["gas"] = estimate*2
    signed = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()
def get_delegator_stake(address):
    delegator_transaction={
        "to": w3.to_checksum_address("0x7abf52a91d3d078960bafc9912fa1be248ef6dcf"),
        "from": "0x0000000000000000000000000000000000000000",
        "data":"0x587cde1e000000000000000000000000"+address[2:]
    }
    result=w3.eth.call(delegator_transaction)
    return "0x"+result.hex()[-40:]
def stake(amount, private_key):
    account = w3.eth.account.from_key(private_key)
    transaction=contract_mock_stake.functions.stake(amount).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 2000000,
        "gasPrice": w3.eth.gas_price*2
    })

    estimate = w3.eth.estimate_gas(transaction, "latest")
    transaction["gas"] = estimate*2
    print(transaction)
    signed = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()
def main():
    with open("private_key.txt", "r") as private_key_file:
        private_keys=private_key_file.readlines()
    for private_key in private_keys:
        account=w3.eth.account.from_key(private_key.strip())
        print(contract_mock_token.functions.balanceOf(account.address).call())
        print(mint_mock(private_key.strip()))
        print(stake(contract_mock_token.functions.balanceOf(account.address).call(), private_key.strip()))
if __name__ == "__main__":
    main()
    