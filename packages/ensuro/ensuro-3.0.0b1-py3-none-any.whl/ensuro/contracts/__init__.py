import os
from pathlib import Path
from ethproto.wrappers import get_provider


def get_contracts_path() -> list:
    return [os.path.abspath(os.path.dirname(__file__))]


def register_contract_path(provider=None):
    if provider is None:
        provider = get_provider()
    for path in get_contracts_path():
        if Path(path) not in provider.artifact_library.lookup_paths:
            provider.artifact_library.lookup_paths.append(Path(path))
