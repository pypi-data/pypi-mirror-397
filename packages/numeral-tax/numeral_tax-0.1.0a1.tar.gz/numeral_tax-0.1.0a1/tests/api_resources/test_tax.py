# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types import TaxPingResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTax:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_ping(self, client: NumeralAPI) -> None:
        tax = client.tax.ping()
        assert_matches_type(TaxPingResponse, tax, path=["response"])

    @parametrize
    def test_method_ping_with_all_params(self, client: NumeralAPI) -> None:
        tax = client.tax.ping(
            x_api_version="2025-05-12",
        )
        assert_matches_type(TaxPingResponse, tax, path=["response"])

    @parametrize
    def test_raw_response_ping(self, client: NumeralAPI) -> None:
        response = client.tax.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tax = response.parse()
        assert_matches_type(TaxPingResponse, tax, path=["response"])

    @parametrize
    def test_streaming_response_ping(self, client: NumeralAPI) -> None:
        with client.tax.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tax = response.parse()
            assert_matches_type(TaxPingResponse, tax, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTax:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_ping(self, async_client: AsyncNumeralAPI) -> None:
        tax = await async_client.tax.ping()
        assert_matches_type(TaxPingResponse, tax, path=["response"])

    @parametrize
    async def test_method_ping_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        tax = await async_client.tax.ping(
            x_api_version="2025-05-12",
        )
        assert_matches_type(TaxPingResponse, tax, path=["response"])

    @parametrize
    async def test_raw_response_ping(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tax = await response.parse()
        assert_matches_type(TaxPingResponse, tax, path=["response"])

    @parametrize
    async def test_streaming_response_ping(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tax = await response.parse()
            assert_matches_type(TaxPingResponse, tax, path=["response"])

        assert cast(Any, response.is_closed) is True
