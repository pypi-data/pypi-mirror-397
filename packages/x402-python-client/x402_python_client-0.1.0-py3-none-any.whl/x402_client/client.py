"""
x402 Python Client - v2 Protocol Implementation
Reads payment requirements from the 'payment-required' header.
"""

import base64
import json
import time
import os
from typing import Optional, Any, Dict
from eth_account import Account
from eth_account.messages import encode_typed_data
import httpx


def create_payment_payload(
    account: Account,
    payment_requirements: Dict,
    resource_url: str,
    x402_version: int = 2
) -> str:
    """
    Create x402 v2 payment payload according to spec.

    The payload structure:
    {
        "x402Version": 2,
        "resource": { "url": "...", "description": "...", "mimeType": "..." },
        "accepted": { ...PaymentRequirements... },
        "payload": {
            "signature": "0x...",
            "authorization": {
                "from": "0x...",
                "to": "0x...",
                "value": "10000",
                "validAfter": "0",
                "validBefore": "1234567890",
                "nonce": "0x..."
            }
        }
    }
    """

    scheme = payment_requirements.get("scheme", "exact")
    network = payment_requirements.get("network", "")
    asset = payment_requirements.get("asset", "")
    amount = payment_requirements.get("amount", "0")
    pay_to = payment_requirements.get("payTo", "")
    max_timeout = payment_requirements.get("maxTimeoutSeconds", 300)
    extra = payment_requirements.get("extra", {})

    # Get chain ID from network string (e.g., "eip155:84532" -> 84532)
    chain_id = int(network.split(":")[-1]) if ":" in network else 1

    # Generate timing and nonce
    valid_after = 0
    valid_before = int(time.time()) + max_timeout
    nonce = os.urandom(32)

    # Create EIP-712 typed data for TransferWithAuthorization (EIP-3009)
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": extra.get("name", "USDC"),
            "version": extra.get("version", "2"),
            "chainId": chain_id,
            "verifyingContract": asset,
        },
        "message": {
            "from": account.address,
            "to": pay_to,
            "value": int(amount),
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce,
        },
    }

    # Sign the typed data
    signable = encode_typed_data(full_message=typed_data)
    signed = account.sign_message(signable)

    # Build the full PaymentPayload per x402 v2 spec
    payment_payload = {
        "x402Version": x402_version,
        "resource": {
            "url": resource_url,
        },
        "accepted": payment_requirements,
        "payload": {
            "signature": "0x" + signed.signature.hex(),
            "authorization": {
                "from": account.address,
                "to": pay_to,
                "value": amount,
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": "0x" + nonce.hex(),
            },
        },
    }

    # Encode as base64
    return base64.b64encode(json.dumps(payment_payload).encode()).decode()


def parse_payment_required_header(header_value: str) -> Dict:
    """
    Parse the payment-required header (base64 encoded JSON).

    Returns the PaymentRequired structure:
    {
        "x402Version": 2,
        "resource": {...},
        "accepts": [...],
        "error": "..."
    }
    """
    return json.loads(base64.b64decode(header_value))


class X402AsyncClient:
    """
    Async HTTP client with x402 v2 payment support.
    Reads payment requirements from the 'payment-required' header.
    """

    def __init__(self, account: Account, **kwargs):
        self.account = account
        self.client_kwargs = kwargs
        self._debug = kwargs.pop("debug", False)

    async def __aenter__(self):
        self._client = httpx.AsyncClient(**self.client_kwargs)
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        # First request
        response = await self._client.request(method, url, **kwargs)

        # If not 402, return as is
        if response.status_code != 402:
            return response

        if self._debug:
            print("[x402] Got 402 Payment Required, processing...")

        # Read payment requirements from header (x402 v2)
        payment_header = response.headers.get("payment-required")
        if not payment_header:
            if self._debug:
                print("[x402] No payment-required header found")
            return response

        try:
            # Parse the payment-required header
            payment_required = parse_payment_required_header(payment_header)

            if self._debug:
                print(f"[x402] x402Version: {payment_required.get('x402Version')}")
                print(f"[x402] accepts: {len(payment_required.get('accepts', []))} options")

            x402_version = payment_required.get("x402Version", 2)
            accepts = payment_required.get("accepts", [])

            if not accepts:
                if self._debug:
                    print("[x402] No payment options in 'accepts'")
                return response

            # Select first payment option
            selected = accepts[0]

            if self._debug:
                print(f"[x402] Selected: {selected.get('scheme')} on {selected.get('network')}")
                print(f"[x402] Amount: {selected.get('amount')} to {selected.get('payTo')}")

            # Create payment payload per x402 v2 spec
            payment_payload = create_payment_payload(
                account=self.account,
                payment_requirements=selected,
                resource_url=str(url),
                x402_version=x402_version
            )

            if self._debug:
                print(f"[x402] Created payment payload, retrying request...")
                # Decode and show the full payload for debugging
                decoded = json.loads(base64.b64decode(payment_payload))
                print(f"[x402] Full payload: {json.dumps(decoded, indent=2)}")

            # Add payment-signature header and retry (x402 v2)
            headers = dict(kwargs.get("headers", {}))
            headers["payment-signature"] = payment_payload
            kwargs["headers"] = headers

            retry_response = await self._client.request(method, url, **kwargs)

            if self._debug:
                print(f"[x402] Retry response: {retry_response.status_code}")
                if retry_response.status_code != 200:
                    print(f"[x402] Retry body: {retry_response.text[:500]}")

            return retry_response

        except Exception as e:
            if self._debug:
                print(f"[x402] Error: {e}")
                import traceback
                traceback.print_exc()
            raise Exception(f"x402 payment failed: {e}")


class X402Client:
    """
    Sync HTTP client with x402 v2 payment support.
    Reads payment requirements from the 'payment-required' header.
    """

    def __init__(self, account: Account, **kwargs):
        self.account = account
        self._debug = kwargs.pop("debug", False)
        self.client_kwargs = kwargs

    def __enter__(self):
        self._client = httpx.Client(**self.client_kwargs)
        return self

    def __exit__(self, *args):
        self._client.close()

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self._request("POST", url, **kwargs)

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self._request("GET", url, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        # First request
        response = self._client.request(method, url, **kwargs)

        # If not 402, return as is
        if response.status_code != 402:
            return response

        if self._debug:
            print("[x402] Got 402 Payment Required, processing...")

        # Read payment requirements from header (x402 v2)
        payment_header = response.headers.get("payment-required")
        if not payment_header:
            if self._debug:
                print("[x402] No payment-required header found")
            return response

        try:
            # Parse the payment-required header
            payment_required = parse_payment_required_header(payment_header)

            if self._debug:
                print(f"[x402] x402Version: {payment_required.get('x402Version')}")

            x402_version = payment_required.get("x402Version", 2)
            accepts = payment_required.get("accepts", [])

            if not accepts:
                return response

            # Select first payment option
            selected = accepts[0]

            # Create payment payload per x402 v2 spec
            payment_payload = create_payment_payload(
                account=self.account,
                payment_requirements=selected,
                resource_url=str(url),
                x402_version=x402_version
            )

            # Add payment-signature header and retry (x402 v2)
            headers = dict(kwargs.get("headers", {}))
            headers["payment-signature"] = payment_payload
            kwargs["headers"] = headers

            retry_response = self._client.request(method, url, **kwargs)
            return retry_response

        except Exception as e:
            if self._debug:
                print(f"[x402] Error: {e}")
            raise Exception(f"x402 payment failed: {e}")
