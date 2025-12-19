"""
Implementation of raydium connector.

Dependencies
------------
* `requests` (HTTP calls to provider)
* `solana` (RPC client + transaction objects)
* `solders` (Public key management)
* `spl` (Associated token address)
"""

from __future__ import annotations

from ..utils.http import create_session_with_retries, DEFAULT_TIMEOUT

from spl.token.instructions import get_associated_token_address

import base64

from solana.rpc.api import VersionedTransaction
from solders.pubkey import Pubkey

import json

class Aggregator:
    def __init__(self, headers: dict = {}, timeout: int = DEFAULT_TIMEOUT):
        self.name = "Raydium"

        self.quote_api = "https://transaction-v1.raydium.io/compute/swap-base-in"
        self.swap_api = "https://transaction-v1.raydium.io/transaction/swap-base-in"
        self.fee_api = "https://api-v3.raydium.io/main/auto-fee"

        self.session = create_session_with_retries(timeout=timeout)
        self.timeout = timeout
        self.headers = headers

    def get_quote(self, **kwargs):
        params = {
            "txVersion": "V0",
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

        response = self.session.get(self.fee_api, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        fee_data = response.json()

        # Get priority_fee with default fallback
        priority_fee = kwargs.get("priority_fee", "medium")
        available_fees = fee_data.get("data", {}).get("default", {})
        
        if priority_fee not in available_fees:
            # Fallback to medium if requested priority not available
            priority_fee = "medium"
        
        fees = available_fees[priority_fee]

        receiver = Pubkey.from_string(kwargs.get("receiver")) if ("receiver" in kwargs) else wallet.pubkey()

        params = json.dumps({
            "txVersion": "V0",
            "wallet": str(wallet.pubkey()),
            "swapResponse": quote,     
            "inputAccount": str(get_associated_token_address(wallet.pubkey(), Pubkey.from_string(quote["data"]["inputMint"]))),
            "outputAccount": str(get_associated_token_address(receiver, Pubkey.from_string(quote["data"]["outputMint"]))),
            "computeUnitPriceMicroLamports": str(fees)
        })

        response = self.session.post(
            self.swap_api, 
            data=params, 
            headers={"Content-Type": "application/json", **self.headers},
            timeout=self.timeout
        )
        response.raise_for_status()
        response_data = response.json()

        trx_list = []
        for record in response_data["data"]:
            trx_decoded = base64.b64decode(record['transaction'])
            trx_versioned = VersionedTransaction.from_bytes(trx_decoded)
            trx_signed = VersionedTransaction(trx_versioned.message, [wallet])

            trx_list.append(trx_signed)
            
        return trx_list
