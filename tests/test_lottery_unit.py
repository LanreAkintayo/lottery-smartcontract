# 1.33 * 10**16 is what I am expecting to be the getEntranceFee
from brownie import accounts, Lottery, config, network, exceptions
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
import pytest

# def test_get_price():
#     account = accounts[0]
#     lottery = Lottery.deploy(
#         config["networks"][network.show_active()]["eth_usd_price_feed_address"],
#         {"from": account},
#     )
#     price = lottery.getPrice()
#     assert price >= Web3.toWei(3700, "ether")
#     assert price < Web3.toWei(3800, "ether")
    

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()

    expected_value = Web3.toWei(0.025, "ether")

    assert entrance_fee == expected_value

def test_cant_enter_unless_started():
    """
    To test, we try to enter before we start.
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    
    entrance_fee = lottery.getEntranceFee() + 100000000

    with pytest.raises(exceptions.VirtualMachineError):
        transaction = lottery.enter({"from": account, "value": entrance_fee})

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery = deploy_lottery()
    account = get_account()

    entrance_fee = lottery.getEntranceFee() + 100000000

    transaction = lottery.startLottery({"from": account})

    transaction2 = lottery.enter({"from": account, "value": entrance_fee})

    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    transaction = fund_with_link(lottery.address)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    lottery = deploy_lottery()

    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(2), "value": lottery.getEntranceFee()})
    transaction = fund_with_link(lottery.address)
    
    transaction = lottery.endLottery({"from": account})

    requestId = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777

    vrf_coordinator_contract = get_contract("vrf_coordinator")

    initial_balance = account.balance()
    
    lottery_balance = lottery.balance()

    vrf_coordinator_contract.callBackWithRandomness(requestId, STATIC_RNG, lottery.address, {"from": account})

    
    assert lottery.winner() == account
    assert account.balance() == initial_balance + lottery_balance
    assert lottery.balance() == 0
    assert lottery.lottery_state() == 1











