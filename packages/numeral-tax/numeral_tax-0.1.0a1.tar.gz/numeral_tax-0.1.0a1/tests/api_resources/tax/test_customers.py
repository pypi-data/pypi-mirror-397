# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.tax import CustomerResponse, CustomerDeleteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCustomers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: NumeralAPI) -> None:
        customer = client.tax.customers.create(
            email="customer@example.com",
        )
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: NumeralAPI) -> None:
        customer = client.tax.customers.create(
            email="customer@example.com",
            is_tax_exempt=True,
            name="Customer Name",
            reference_customer_id="20506",
        )
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: NumeralAPI) -> None:
        response = client.tax.customers.with_raw_response.create(
            email="customer@example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: NumeralAPI) -> None:
        with client.tax.customers.with_streaming_response.create(
            email="customer@example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerResponse, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: NumeralAPI) -> None:
        customer = client.tax.customers.retrieve(
            "cus_1234-65423",
        )
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: NumeralAPI) -> None:
        response = client.tax.customers.with_raw_response.retrieve(
            "cus_1234-65423",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: NumeralAPI) -> None:
        with client.tax.customers.with_streaming_response.retrieve(
            "cus_1234-65423",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerResponse, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.tax.customers.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_delete(self, client: NumeralAPI) -> None:
        customer = client.tax.customers.delete(
            "cus_1234-65423",
        )
        assert_matches_type(CustomerDeleteResponse, customer, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: NumeralAPI) -> None:
        response = client.tax.customers.with_raw_response.delete(
            "cus_1234-65423",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = response.parse()
        assert_matches_type(CustomerDeleteResponse, customer, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: NumeralAPI) -> None:
        with client.tax.customers.with_streaming_response.delete(
            "cus_1234-65423",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = response.parse()
            assert_matches_type(CustomerDeleteResponse, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.tax.customers.with_raw_response.delete(
                "",
            )


class TestAsyncCustomers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncNumeralAPI) -> None:
        customer = await async_client.tax.customers.create(
            email="customer@example.com",
        )
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        customer = await async_client.tax.customers.create(
            email="customer@example.com",
            is_tax_exempt=True,
            name="Customer Name",
            reference_customer_id="20506",
        )
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.customers.with_raw_response.create(
            email="customer@example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.customers.with_streaming_response.create(
            email="customer@example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerResponse, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        customer = await async_client.tax.customers.retrieve(
            "cus_1234-65423",
        )
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.customers.with_raw_response.retrieve(
            "cus_1234-65423",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerResponse, customer, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.customers.with_streaming_response.retrieve(
            "cus_1234-65423",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerResponse, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.tax.customers.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncNumeralAPI) -> None:
        customer = await async_client.tax.customers.delete(
            "cus_1234-65423",
        )
        assert_matches_type(CustomerDeleteResponse, customer, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.customers.with_raw_response.delete(
            "cus_1234-65423",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        customer = await response.parse()
        assert_matches_type(CustomerDeleteResponse, customer, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.customers.with_streaming_response.delete(
            "cus_1234-65423",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            customer = await response.parse()
            assert_matches_type(CustomerDeleteResponse, customer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.tax.customers.with_raw_response.delete(
                "",
            )
