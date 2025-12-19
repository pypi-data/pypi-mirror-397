# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from numeral_tax import NumeralAPI, AsyncNumeralAPI
from tests.utils import assert_matches_type
from numeral_tax.types.tax import (
    ProductResponse,
    ProductListResponse,
    DeleteProductResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProducts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: NumeralAPI) -> None:
        product = client.tax.products.create(
            product_category="CLOTHING_GENERAL",
            reference_product_id="p-123456789",
            reference_product_name="Red Shoes",
        )
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: NumeralAPI) -> None:
        response = client.tax.products.with_raw_response.create(
            product_category="CLOTHING_GENERAL",
            reference_product_id="p-123456789",
            reference_product_name="Red Shoes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = response.parse()
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: NumeralAPI) -> None:
        with client.tax.products.with_streaming_response.create(
            product_category="CLOTHING_GENERAL",
            reference_product_id="p-123456789",
            reference_product_name="Red Shoes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = response.parse()
            assert_matches_type(ProductResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: NumeralAPI) -> None:
        product = client.tax.products.retrieve(
            "p-20506",
        )
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: NumeralAPI) -> None:
        response = client.tax.products.with_raw_response.retrieve(
            "p-20506",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = response.parse()
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: NumeralAPI) -> None:
        with client.tax.products.with_streaming_response.retrieve(
            "p-20506",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = response.parse()
            assert_matches_type(ProductResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `reference_product_id` but received ''"):
            client.tax.products.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: NumeralAPI) -> None:
        product = client.tax.products.list()
        assert_matches_type(ProductListResponse, product, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: NumeralAPI) -> None:
        product = client.tax.products.list(
            cursor="cursor",
        )
        assert_matches_type(ProductListResponse, product, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: NumeralAPI) -> None:
        response = client.tax.products.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = response.parse()
        assert_matches_type(ProductListResponse, product, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: NumeralAPI) -> None:
        with client.tax.products.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = response.parse()
            assert_matches_type(ProductListResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: NumeralAPI) -> None:
        product = client.tax.products.delete(
            "p-309",
        )
        assert_matches_type(DeleteProductResponse, product, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: NumeralAPI) -> None:
        response = client.tax.products.with_raw_response.delete(
            "p-309",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = response.parse()
        assert_matches_type(DeleteProductResponse, product, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: NumeralAPI) -> None:
        with client.tax.products.with_streaming_response.delete(
            "p-309",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = response.parse()
            assert_matches_type(DeleteProductResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: NumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `reference_product_id` but received ''"):
            client.tax.products.with_raw_response.delete(
                "",
            )


class TestAsyncProducts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncNumeralAPI) -> None:
        product = await async_client.tax.products.create(
            product_category="CLOTHING_GENERAL",
            reference_product_id="p-123456789",
            reference_product_name="Red Shoes",
        )
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.products.with_raw_response.create(
            product_category="CLOTHING_GENERAL",
            reference_product_id="p-123456789",
            reference_product_name="Red Shoes",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = await response.parse()
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.products.with_streaming_response.create(
            product_category="CLOTHING_GENERAL",
            reference_product_id="p-123456789",
            reference_product_name="Red Shoes",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = await response.parse()
            assert_matches_type(ProductResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        product = await async_client.tax.products.retrieve(
            "p-20506",
        )
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.products.with_raw_response.retrieve(
            "p-20506",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = await response.parse()
        assert_matches_type(ProductResponse, product, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.products.with_streaming_response.retrieve(
            "p-20506",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = await response.parse()
            assert_matches_type(ProductResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `reference_product_id` but received ''"):
            await async_client.tax.products.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncNumeralAPI) -> None:
        product = await async_client.tax.products.list()
        assert_matches_type(ProductListResponse, product, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNumeralAPI) -> None:
        product = await async_client.tax.products.list(
            cursor="cursor",
        )
        assert_matches_type(ProductListResponse, product, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.products.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = await response.parse()
        assert_matches_type(ProductListResponse, product, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.products.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = await response.parse()
            assert_matches_type(ProductListResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncNumeralAPI) -> None:
        product = await async_client.tax.products.delete(
            "p-309",
        )
        assert_matches_type(DeleteProductResponse, product, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNumeralAPI) -> None:
        response = await async_client.tax.products.with_raw_response.delete(
            "p-309",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = await response.parse()
        assert_matches_type(DeleteProductResponse, product, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNumeralAPI) -> None:
        async with async_client.tax.products.with_streaming_response.delete(
            "p-309",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = await response.parse()
            assert_matches_type(DeleteProductResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNumeralAPI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `reference_product_id` but received ''"):
            await async_client.tax.products.with_raw_response.delete(
                "",
            )
