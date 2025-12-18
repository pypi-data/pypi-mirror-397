import os
from pathlib import Path

import ensuro
from ensuro import wrappers

CONTRACTS_PATH = os.path.join(
    os.path.abspath(os.path.dirname(ensuro.__file__)), "contracts"
)


def test_get_contracts_path():
    assert ensuro.get_contracts_path() == [CONTRACTS_PATH]


def test_register_contract_path():
    provider = wrappers.get_provider("w3")
    assert provider.artifact_library.lookup_paths == []
    ensuro.register_contract_path(provider)
    assert provider.artifact_library.lookup_paths == [Path(CONTRACTS_PATH)]
