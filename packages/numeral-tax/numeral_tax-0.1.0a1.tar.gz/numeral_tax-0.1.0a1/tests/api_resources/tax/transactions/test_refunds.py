# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.tax.transactions import RefundListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRefunds:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: NumeralAPI) -> None:
        refund = client.tax.transactions.refunds.list(
            "transaction_id",
        )
        assert_matches_type(RefundListResponse, refund, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: NumeralAPI) -> None:
        response = client.tax.transactions.refunds.with_raw_response.list(
            "transaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        refund = response.parse()
        assert_matches_type(RefundListResponse, refund, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: NumeralAPI) -> None:
        with client.tax.transactions.refunds.with_streaming_response.list(
            "transaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            refund = response.parse()
            assert_matches_type(RefundListResponse, refund, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transaction_id` but received ''"):
            client.tax.transactions.refunds.with_raw_response.list(
                "",
            )


class TestAsyncRefunds:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncNumeralAPI) -> None:
        refund = await async_client.tax.transactions.refunds.list(
            "transaction_id",
        )
        assert_matches_type(RefundListResponse, refund, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.transactions.refunds.with_raw_response.list(
            "transaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        refund = await response.parse()
        assert_matches_type(RefundListResponse, refund, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.transactions.refunds.with_streaming_response.list(
            "transaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            refund = await response.parse()
            assert_matches_type(RefundListResponse, refund, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transaction_id` but received ''"):
            await async_client.tax.transactions.refunds.with_raw_response.list(
                "",
            )
