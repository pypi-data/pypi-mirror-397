"""
Implementation of jupiter connector.

Dependencies
------------
* `requests` (HTTP calls to provider)
* `solana` (RPC client + transaction objects)
"""

from __future__ import annotations

from ..utils.http import create_session_with_retries, DEFAULT_TIMEOUT

import base64

from solana.rpc.api import VersionedTransaction

import json

class Aggregator:
    def __init__(self, headers: dict = {}, timeout: int = DEFAULT_TIMEOUT):
        self.name = "Jupiter"

        self.quote_api = "https://quote-api.jup.ag/v6/quote"
        self.swap_api = "https://quote-api.jup.ag/v6/swap"

        self.session = create_session_with_retries(timeout=timeout)
        self.timeout = timeout
        self.headers = headers

    def get_quote(self, **kwargs):
        params = {
            "swapMode": "ExactIn",
            "inputMint": kwargs.get("source_token"),
            "outputMint": kwargs.get("destination_token"),
            "amount": kwargs.get("source_amount"),
        }
        
        if ("slippage" in kwargs):
            params["slippageBps"] = kwargs.get("slippage")

        response = self.session.get(
            self.quote_api, 
            params=params, 
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return response.json()

    def get_swap(self, **kwargs):
        quote = kwargs.get("quote").quote
        wallet = kwargs.get("chain").wallet

        params = json.dumps({
            "userPublicKey": str(wallet.pubkey()),
            "quoteResponse": quote,        
        })

        response = self.session.post(
            self.swap_api, 
            data=params, 
            headers={"Content-Type": "application/json", **self.headers},
            timeout=self.timeout
        )
        response.raise_for_status()
        response_data = response.json()

        trx_decoded = base64.b64decode(response_data.get("swapTransaction"))
        trx_versioned = VersionedTransaction.from_bytes(trx_decoded)  
        trx_signed = VersionedTransaction(trx_versioned.message, [wallet])

        return [trx_signed]
