from brownie import network
import pytest
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from scripts.deploy_lottery import deploy_lottery

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    
    account = get_account()

    lottery = deploy_lottery()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    
    fund_with_link(lottery.address, account=account)
    lottery.endLottery({"from": account})
    time.sleep(60)

    assert lottery.winner() == account
    assert lottery.balance() == 0


    