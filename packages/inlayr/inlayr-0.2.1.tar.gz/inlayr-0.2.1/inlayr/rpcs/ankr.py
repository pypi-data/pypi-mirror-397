"""
Implementation of ankr connector.

Dependencies
------------
* `web3` (interaction with chains)
"""

from __future__ import annotations

from ..utils.validation import validate_chain_id
from web3 import Web3, HTTPProvider

class RPC:
    def __init__(self, chain_id: int | None, api_key: str, headers: dict = {}):
        self.name = "ankr"

        self.chain_id = chain_id
        self.api_key = api_key
        self.headers = headers

        self.chain_dict = {
            1:  "eth",
            17000: "eth_holesky",
            11155111: "eth_sepolia",
            56: "bsc",
            137: "polygon",
            1101: "polygon_zkevm",
            43114: "avalanche",
            42161: "arbitrum",
            1284: "moonbeam",
            10: "optimism",
            100: "gnosis",
            8453: "base",
            59144: "linea",
            534352: "scroll",
            250: "fantom",
            42220: "celo",
            1666600000: "harmony",
        }

        validate_chain_id(self.chain_id, self.chain_dict)

        self.rpc_url = f"https://rpc.ankr.com/{self.chain_dict[self.chain_id]}/{self.api_key}"

        self.client = Web3(HTTPProvider(self.rpc_url))
