# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.tax import TransactionResponse, DeleteTransactionResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTransactions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: NumeralAPI) -> None:
        transaction = client.tax.transactions.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
        )
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: NumeralAPI) -> None:
        transaction = client.tax.transactions.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
            metadata={"example_key": "example_value"},
            transaction_processed_at=1714787673,
        )
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: NumeralAPI) -> None:
        response = client.tax.transactions.with_raw_response.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = response.parse()
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: NumeralAPI) -> None:
        with client.tax.transactions.with_streaming_response.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = response.parse()
            assert_matches_type(TransactionResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: NumeralAPI) -> None:
        transaction = client.tax.transactions.retrieve(
            "tr_172175669911564a621fc-ab56-441b-959f-7b2587cc72f2",
        )
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: NumeralAPI) -> None:
        response = client.tax.transactions.with_raw_response.retrieve(
            "tr_172175669911564a621fc-ab56-441b-959f-7b2587cc72f2",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = response.parse()
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: NumeralAPI) -> None:
        with client.tax.transactions.with_streaming_response.retrieve(
            "tr_172175669911564a621fc-ab56-441b-959f-7b2587cc72f2",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = response.parse()
            assert_matches_type(TransactionResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transaction_id` but received ''"):
            client.tax.transactions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_delete(self, client: NumeralAPI) -> None:
        transaction = client.tax.transactions.delete(
            "tr_1721782517712b5926847-d313-4721-9ee2-f8bde575d80b",
        )
        assert_matches_type(DeleteTransactionResponse, transaction, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: NumeralAPI) -> None:
        response = client.tax.transactions.with_raw_response.delete(
            "tr_1721782517712b5926847-d313-4721-9ee2-f8bde575d80b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = response.parse()
        assert_matches_type(DeleteTransactionResponse, transaction, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: NumeralAPI) -> None:
        with client.tax.transactions.with_streaming_response.delete(
            "tr_1721782517712b5926847-d313-4721-9ee2-f8bde575d80b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = response.parse()
            assert_matches_type(DeleteTransactionResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transaction_id` but received ''"):
            client.tax.transactions.with_raw_response.delete(
                "",
            )


class TestAsyncTransactions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncNumeralAPI) -> None:
        transaction = await async_client.tax.transactions.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
        )
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        transaction = await async_client.tax.transactions.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
            metadata={"example_key": "example_value"},
            transaction_processed_at=1714787673,
        )
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.transactions.with_raw_response.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = await response.parse()
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.transactions.with_streaming_response.create(
            calculation_id="calc_123456789",
            reference_order_id="343-45836",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = await response.parse()
            assert_matches_type(TransactionResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        transaction = await async_client.tax.transactions.retrieve(
            "tr_172175669911564a621fc-ab56-441b-959f-7b2587cc72f2",
        )
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.transactions.with_raw_response.retrieve(
            "tr_172175669911564a621fc-ab56-441b-959f-7b2587cc72f2",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = await response.parse()
        assert_matches_type(TransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.transactions.with_streaming_response.retrieve(
            "tr_172175669911564a621fc-ab56-441b-959f-7b2587cc72f2",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = await response.parse()
            assert_matches_type(TransactionResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transaction_id` but received ''"):
            await async_client.tax.transactions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncNumeralAPI) -> None:
        transaction = await async_client.tax.transactions.delete(
            "tr_1721782517712b5926847-d313-4721-9ee2-f8bde575d80b",
        )
        assert_matches_type(DeleteTransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.transactions.with_raw_response.delete(
            "tr_1721782517712b5926847-d313-4721-9ee2-f8bde575d80b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transaction = await response.parse()
        assert_matches_type(DeleteTransactionResponse, transaction, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.transactions.with_streaming_response.delete(
            "tr_1721782517712b5926847-d313-4721-9ee2-f8bde575d80b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transaction = await response.parse()
            assert_matches_type(DeleteTransactionResponse, transaction, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `transaction_id` but received ''"):
            await async_client.tax.transactions.with_raw_response.delete(
                "",
            )
