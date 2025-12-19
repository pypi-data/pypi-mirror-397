# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.shared import RefundResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRefunds:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: NumeralAPI) -> None:
        refund = client.tax.refunds.create(
            transaction_id="tr_123456789",
            type="partial",
        )
        assert_matches_type(RefundResponse, refund, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: NumeralAPI) -> None:
        refund = client.tax.refunds.create(
            transaction_id="tr_123456789",
            type="partial",
            line_items=[
                {
                    "quantity": 2,
                    "reference_line_item_id": "line_123456789",
                    "reference_product_id": "p-1233543",
                    "sales_amount_refunded": -200,
                    "tax_amount_refunded": -14,
                }
            ],
            refund_processed_at=1714787673,
        )
        assert_matches_type(RefundResponse, refund, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: NumeralAPI) -> None:
        response = client.tax.refunds.with_raw_response.create(
            transaction_id="tr_123456789",
            type="partial",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        refund = response.parse()
        assert_matches_type(RefundResponse, refund, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: NumeralAPI) -> None:
        with client.tax.refunds.with_streaming_response.create(
            transaction_id="tr_123456789",
            type="partial",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            refund = response.parse()
            assert_matches_type(RefundResponse, refund, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRefunds:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncNumeralAPI) -> None:
        refund = await async_client.tax.refunds.create(
            transaction_id="tr_123456789",
            type="partial",
        )
        assert_matches_type(RefundResponse, refund, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        refund = await async_client.tax.refunds.create(
            transaction_id="tr_123456789",
            type="partial",
            line_items=[
                {
                    "quantity": 2,
                    "reference_line_item_id": "line_123456789",
                    "reference_product_id": "p-1233543",
                    "sales_amount_refunded": -200,
                    "tax_amount_refunded": -14,
                }
            ],
            refund_processed_at=1714787673,
        )
        assert_matches_type(RefundResponse, refund, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.refunds.with_raw_response.create(
            transaction_id="tr_123456789",
            type="partial",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        refund = await response.parse()
        assert_matches_type(RefundResponse, refund, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.refunds.with_streaming_response.create(
            transaction_id="tr_123456789",
            type="partial",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            refund = await response.parse()
            assert_matches_type(RefundResponse, refund, path=["response"])

        assert cast(Any, response.is_closed) is True
