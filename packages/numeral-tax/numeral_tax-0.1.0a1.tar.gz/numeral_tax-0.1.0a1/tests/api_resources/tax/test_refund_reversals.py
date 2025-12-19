# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.shared import RefundResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRefundReversals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: NumeralAPI) -> None:
        refund_reversal = client.tax.refund_reversals.create()
        assert_matches_type(RefundResponse, refund_reversal, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: NumeralAPI) -> None:
        refund_reversal = client.tax.refund_reversals.create(
            refund_id="ref_tr_123456789",
        )
        assert_matches_type(RefundResponse, refund_reversal, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: NumeralAPI) -> None:
        response = client.tax.refund_reversals.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        refund_reversal = response.parse()
        assert_matches_type(RefundResponse, refund_reversal, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: NumeralAPI) -> None:
        with client.tax.refund_reversals.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            refund_reversal = response.parse()
            assert_matches_type(RefundResponse, refund_reversal, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRefundReversals:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncNumeralAPI) -> None:
        refund_reversal = await async_client.tax.refund_reversals.create()
        assert_matches_type(RefundResponse, refund_reversal, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        refund_reversal = await async_client.tax.refund_reversals.create(
            refund_id="ref_tr_123456789",
        )
        assert_matches_type(RefundResponse, refund_reversal, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.refund_reversals.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        refund_reversal = await response.parse()
        assert_matches_type(RefundResponse, refund_reversal, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.refund_reversals.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            refund_reversal = await response.parse()
            assert_matches_type(RefundResponse, refund_reversal, path=["response"])

        assert cast(Any, response.is_closed) is True
