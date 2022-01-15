from brownie import Lottery, accounts, config, network
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
import time

def deploy_lottery():
    """
    1. Get an account that will deploy
    2. Deploy the lottery

    address _price_feed, # MockV3Aggregator gives the price feed for a local network
    address _vrfCoordinator,
    address _link,
    uint256 _fee,
    bytes32 _keyHash

    """

    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed_address").address,
        get_contract("vrf_coordinator").address,
        get_contract("link").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["key_hash"],
        {"from": account},
        publish_source = config["networks"][network.show_active()].get("verify", False)
    )

    print("Lottery has been deployed")
    return lottery

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    transaction = lottery.startLottery({"from": account})
    transaction.wait(1)
    return lottery.lottery_state()
    print("Lottery has been started")

def enter_lottery():
    account = get_account()   
    lottery = Lottery[-1]
    entrance_fee = lottery.getEntranceFee() + 100000000
    transaction = lottery.enter({"from": account, "value": entrance_fee})
    transaction.wait(1)
    return lottery.lottery_state()
    print("Lottery has been entered!")

def end_lottery():
    """
    Here, We will need to fund the contract because the contract called requestRandomness(keyHash, fee) here. 
    1. Let's fund the contract
    """
    account = get_account()
    lottery = Lottery[-1]

    # 1
    transaction1 = fund_with_link(lottery.address)
    transaction1.wait(1)
    print(f"Lottery with address: {lottery.address} has been funded")

    transaction2 = lottery.endLottery()
    transaction2.wait(1)
    print("Lottery has ended")

    time.sleep(100)  # sleep for 60 seconds
    print(f"The winner of the lottery is {lottery.winner()}")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()