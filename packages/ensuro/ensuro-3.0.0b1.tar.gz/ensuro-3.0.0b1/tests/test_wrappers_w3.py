from io import StringIO

import pytest

import ensuro
from ensuro import wrappers
from ensuro.utils import load_config


@pytest.fixture(autouse=True)
def w3provider():
    try:
        from ethproto import w3wrappers
    except Exception:
        raise pytest.skip("web3py not installed")

    contracts_json_path = ensuro.get_contracts_path()
    provider = w3wrappers.register_w3_provider(
        provider_kwargs={"contracts_path": contracts_json_path},
        tester=True,
    )

    return provider


@pytest.mark.parametrize(
    "contract_name",
    ["PolicyPool", "RiskModule", "EToken", "PremiumsAccount"],
)
def test_get_contract(contract_name):
    provider = wrappers.get_provider()
    contract = provider.get_contract_def(contract_name)
    assert contract.contract_name == contract_name
    assert len(contract.abi) > 0


def test_load_yaml_w3():
    YAML_SETUP = """
    risk_modules:
      - name: Roulette
        coll_ratio: 1
        sr_roc: "0.01"
        ensuro_pp_fee: 0
        roles:
          - user: owner
            role: PRICER_ROLE
          - user: owner
            role: RESOLVER_ROLE
    currency:
        name: USD
        symbol: $
        initial_supply: 6000
        initial_balances:
        - user: LP1
          amount: 3503
        - user: CUST1
          amount: 100
    etokens:
      - name: eUSD1YEAR
    """

    pool = load_config(StringIO(YAML_SETUP), ensuro.wrappers)
    assert "eUSD1YEAR" in pool.etokens
    assert "Roulette" in pool.risk_modules
