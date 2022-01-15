from brownie import accounts, network, Contract, MockV3Aggregator, interface , LinkToken, VRFCoordinatorMock,config

FORKED_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["ganache-local", "development"]


def get_account(index=None, id=None):
    """
    1. if index is specified, use accounts[index]
    2. if accountId is specified, use that account
    3. if we are on a development environment, use accounts[0]
    4. if we are on a test network generate your account from the private key in brownie-config.yaml,
    """

    # 1
    if index:
        return accounts[index]

    # 2
    if id:
        return accounts.load(id)

    # 3
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_BLOCKCHAIN_ENVIRONMENTS
    ):
        return accounts[0]

    # 4
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed_address": MockV3Aggregator,
    "link": LinkToken,
    "vrf_coordinator": VRFCoordinatorMock,
}


def get_contract(contract_name):
    """
    Our goal is to return a contract here depepending on whether we are on a real network or a local network.

    1. If are dealing with LOCAL_BLOCKCHAIN_ENVIROMENT/local network, we deploy a Mock contract and we obtain the most recently deployed Mock contract.

    2. If we are on a real network, we are going to grab the contact address of the contract and return a mock contract based on the contract address and abi of the particular mock.

    contract_name = eth_usd_price_feed_address
    contract_address = "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419" (this gives the price feed address of a real network)
    contract_type = MockV3Aggregator(to obtain the price feed address) if we are working on a local network
    """

    contract_type = contract_to_mock[contract_name]

    # 1
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]

    # 2. We make use of the Mock version and the contract_address to generate a contract
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
STARTING_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, starting_value=STARTING_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, starting_value, {"from": account})
    link_contract = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_contract.address, {"from": account})

    print("Mock Deployed!")

def fund_with_link(contract_address, link_token_contract=None, account=None, amount=100000000000000000):
    
    link_token_contract = link_token_contract if link_token_contract else get_contract("link")
    account = account if account else get_account()

    transaction = link_token_contract.transfer(contract_address, amount, {"from": account})

    return transaction

    # I can also obtain a link_token_contract if I have the Link_Token interface.

