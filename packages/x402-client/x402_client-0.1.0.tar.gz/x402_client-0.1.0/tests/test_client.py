"""Tests for x402_client."""

import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from eth_account import Account

from x402_client import (
    X402AsyncClient,
    X402Client,
    create_payment_payload,
    parse_payment_required_header,
)


# Test account (DO NOT use in production)
TEST_PRIVATE_KEY = "0x" + "1" * 64
TEST_ACCOUNT = Account.from_key(TEST_PRIVATE_KEY)


class TestParsePaymentRequiredHeader:
    """Tests for parse_payment_required_header function."""

    def test_parse_valid_header(self):
        """Should parse a valid base64 encoded payment-required header."""
        payment_data = {
            "x402Version": 2,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "eip155:84532",
                    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                    "amount": "10000",
                    "payTo": "0x1234567890123456789012345678901234567890",
                    "maxTimeoutSeconds": 300,
                }
            ],
        }
        encoded = base64.b64encode(json.dumps(payment_data).encode()).decode()

        result = parse_payment_required_header(encoded)

        assert result["x402Version"] == 2
        assert len(result["accepts"]) == 1
        assert result["accepts"][0]["scheme"] == "exact"
        assert result["accepts"][0]["network"] == "eip155:84532"

    def test_parse_invalid_base64(self):
        """Should raise error for invalid base64."""
        with pytest.raises(Exception):
            parse_payment_required_header("not-valid-base64!!!")

    def test_parse_invalid_json(self):
        """Should raise error for invalid JSON after decoding."""
        invalid_json = base64.b64encode(b"not json").decode()
        with pytest.raises(json.JSONDecodeError):
            parse_payment_required_header(invalid_json)


class TestCreatePaymentPayload:
    """Tests for create_payment_payload function."""

    def test_create_payload_structure(self):
        """Should create a valid x402 v2 payment payload."""
        payment_requirements = {
            "scheme": "exact",
            "network": "eip155:84532",
            "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
            "amount": "10000",
            "payTo": "0x1234567890123456789012345678901234567890",
            "maxTimeoutSeconds": 300,
            "extra": {"name": "USDC", "version": "2"},
        }

        result = create_payment_payload(
            account=TEST_ACCOUNT,
            payment_requirements=payment_requirements,
            resource_url="https://api.example.com/resource",
        )

        # Decode and verify structure
        decoded = json.loads(base64.b64decode(result))

        assert decoded["x402Version"] == 2
        assert decoded["resource"]["url"] == "https://api.example.com/resource"
        assert decoded["accepted"] == payment_requirements
        assert "payload" in decoded
        assert "signature" in decoded["payload"]
        assert decoded["payload"]["signature"].startswith("0x")

        auth = decoded["payload"]["authorization"]
        assert auth["from"] == TEST_ACCOUNT.address
        assert auth["to"] == payment_requirements["payTo"]
        assert auth["value"] == "10000"
        assert auth["nonce"].startswith("0x")

    def test_create_payload_with_different_chain(self):
        """Should correctly parse chain ID from network string."""
        payment_requirements = {
            "scheme": "exact",
            "network": "eip155:1",  # Mainnet
            "asset": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC on mainnet
            "amount": "5000",
            "payTo": "0x1234567890123456789012345678901234567890",
            "maxTimeoutSeconds": 60,
        }

        result = create_payment_payload(
            account=TEST_ACCOUNT,
            payment_requirements=payment_requirements,
            resource_url="https://example.com",
            x402_version=2,
        )

        decoded = json.loads(base64.b64decode(result))
        assert decoded["x402Version"] == 2


class TestX402AsyncClient:
    """Tests for X402AsyncClient."""

    @pytest.mark.asyncio
    async def test_non_402_response_passthrough(self):
        """Should pass through non-402 responses without modification."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            MockClient.return_value = mock_client

            async with X402AsyncClient(account=TEST_ACCOUNT) as client:
                client._client = mock_client
                response = await client.get("https://api.example.com/free")

            assert response.status_code == 200
            assert response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_402_without_header_passthrough(self):
        """Should pass through 402 without payment-required header."""
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            MockClient.return_value = mock_client

            async with X402AsyncClient(account=TEST_ACCOUNT) as client:
                client._client = mock_client
                response = await client.get("https://api.example.com/paid")

            assert response.status_code == 402

    @pytest.mark.asyncio
    async def test_402_with_payment_flow(self):
        """Should handle 402 and retry with payment."""
        payment_data = {
            "x402Version": 2,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "eip155:84532",
                    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                    "amount": "10000",
                    "payTo": "0x1234567890123456789012345678901234567890",
                    "maxTimeoutSeconds": 300,
                    "extra": {"name": "USDC", "version": "2"},
                }
            ],
        }
        encoded_payment = base64.b64encode(json.dumps(payment_data).encode()).decode()

        mock_402_response = MagicMock()
        mock_402_response.status_code = 402
        mock_402_response.headers = {"payment-required": encoded_payment}

        mock_success_response = MagicMock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {"data": "success"}

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request.side_effect = [mock_402_response, mock_success_response]
            MockClient.return_value = mock_client

            async with X402AsyncClient(account=TEST_ACCOUNT) as client:
                client._client = mock_client
                response = await client.post(
                    "https://api.example.com/paid",
                    json={"param": "value"}
                )

            assert response.status_code == 200
            assert mock_client.request.call_count == 2

            # Verify payment-signature header was added on retry
            retry_call = mock_client.request.call_args_list[1]
            assert "payment-signature" in retry_call.kwargs["headers"]


class TestX402Client:
    """Tests for X402Client (sync)."""

    def test_non_402_response_passthrough(self):
        """Should pass through non-402 responses without modification."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch("httpx.Client") as MockClient:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            MockClient.return_value = mock_client

            with X402Client(account=TEST_ACCOUNT) as client:
                client._client = mock_client
                response = client.get("https://api.example.com/free")

            assert response.status_code == 200

    def test_402_without_header_passthrough(self):
        """Should pass through 402 without payment-required header."""
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.headers = {}

        with patch("httpx.Client") as MockClient:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            MockClient.return_value = mock_client

            with X402Client(account=TEST_ACCOUNT) as client:
                client._client = mock_client
                response = client.get("https://api.example.com/paid")

            assert response.status_code == 402


class TestDebugMode:
    """Tests for debug mode."""

    @pytest.mark.asyncio
    async def test_debug_mode_prints(self, capsys):
        """Should print debug messages when debug=True."""
        payment_data = {
            "x402Version": 2,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "eip155:84532",
                    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                    "amount": "10000",
                    "payTo": "0x1234567890123456789012345678901234567890",
                    "maxTimeoutSeconds": 300,
                    "extra": {"name": "USDC", "version": "2"},
                }
            ],
        }
        encoded_payment = base64.b64encode(json.dumps(payment_data).encode()).decode()

        mock_402_response = MagicMock()
        mock_402_response.status_code = 402
        mock_402_response.headers = {"payment-required": encoded_payment}

        mock_success_response = MagicMock()
        mock_success_response.status_code = 200

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request.side_effect = [mock_402_response, mock_success_response]
            MockClient.return_value = mock_client

            async with X402AsyncClient(account=TEST_ACCOUNT, debug=True) as client:
                client._client = mock_client
                await client.get("https://api.example.com/paid")

            captured = capsys.readouterr()
            assert "[x402]" in captured.out
            assert "402 Payment Required" in captured.out
