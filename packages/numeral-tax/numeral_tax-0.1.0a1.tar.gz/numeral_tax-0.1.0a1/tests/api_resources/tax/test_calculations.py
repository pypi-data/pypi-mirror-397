# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.tax import CalculationResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCalculations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: NumeralAPI) -> None:
        calculation = client.tax.calculations.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                }
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                    }
                ],
                "tax_included_in_amount": False,
            },
        )
        assert_matches_type(CalculationResponse, calculation, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: NumeralAPI) -> None:
        calculation = client.tax.calculations.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                    "address_line_2": "Unit 2",
                },
                "id": "cus_123456789",
                "tax_ids": [
                    {
                        "type": "VAT",
                        "value": "value",
                    }
                ],
                "type": "CONSUMER",
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                        "product_category": "GENERAL_MERCHANDISE",
                        "reference_line_item_id": "line_123456789",
                        "reference_product_id": "wand_elder_12",
                    }
                ],
                "tax_included_in_amount": False,
                "automatic_tax": "auto",
            },
            metadata={"example_key": "example_value"},
            origin_address={
                "address_city": "Danville",
                "address_country": "US",
                "address_line_1": "3990 N County Rd 300 E",
                "address_postal_code": "46122",
                "address_province": "IN",
                "address_line_2": "Unit 2",
            },
            x_api_version="2025-05-12",
        )
        assert_matches_type(CalculationResponse, calculation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: NumeralAPI) -> None:
        response = client.tax.calculations.with_raw_response.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                }
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                    }
                ],
                "tax_included_in_amount": False,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        calculation = response.parse()
        assert_matches_type(CalculationResponse, calculation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: NumeralAPI) -> None:
        with client.tax.calculations.with_streaming_response.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                }
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                    }
                ],
                "tax_included_in_amount": False,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            calculation = response.parse()
            assert_matches_type(CalculationResponse, calculation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCalculations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncNumeralAPI) -> None:
        calculation = await async_client.tax.calculations.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                }
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                    }
                ],
                "tax_included_in_amount": False,
            },
        )
        assert_matches_type(CalculationResponse, calculation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        calculation = await async_client.tax.calculations.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                    "address_line_2": "Unit 2",
                },
                "id": "cus_123456789",
                "tax_ids": [
                    {
                        "type": "VAT",
                        "value": "value",
                    }
                ],
                "type": "CONSUMER",
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                        "product_category": "GENERAL_MERCHANDISE",
                        "reference_line_item_id": "line_123456789",
                        "reference_product_id": "wand_elder_12",
                    }
                ],
                "tax_included_in_amount": False,
                "automatic_tax": "auto",
            },
            metadata={"example_key": "example_value"},
            origin_address={
                "address_city": "Danville",
                "address_country": "US",
                "address_line_1": "3990 N County Rd 300 E",
                "address_postal_code": "46122",
                "address_province": "IN",
                "address_line_2": "Unit 2",
            },
            x_api_version="2025-05-12",
        )
        assert_matches_type(CalculationResponse, calculation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.calculations.with_raw_response.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                }
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                    }
                ],
                "tax_included_in_amount": False,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        calculation = await response.parse()
        assert_matches_type(CalculationResponse, calculation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.calculations.with_streaming_response.create(
            customer={
                "address": {
                    "address_city": "Little Whinging",
                    "address_country": "US",
                    "address_line_1": "4 Privet Drive",
                    "address_postal_code": "90210",
                    "address_province": "CA",
                    "address_type": "shipping",
                }
            },
            order_details={
                "customer_currency_code": "USD",
                "line_items": [
                    {
                        "amount": 10000,
                        "quantity": 1,
                    }
                ],
                "tax_included_in_amount": False,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            calculation = await response.parse()
            assert_matches_type(CalculationResponse, calculation, path=["response"])

        assert cast(Any, response.is_closed) is True
