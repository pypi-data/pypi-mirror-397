# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .refunds import (
    RefundsResource,
    AsyncRefundsResource,
    RefundsResourceWithRawResponse,
    AsyncRefundsResourceWithRawResponse,
    RefundsResourceWithStreamingResponse,
    AsyncRefundsResourceWithStreamingResponse,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import is_given, strip_not_given
from .products import (
    ProductsResource,
    AsyncProductsResource,
    ProductsResourceWithRawResponse,
    AsyncProductsResourceWithRawResponse,
    ProductsResourceWithStreamingResponse,
    AsyncProductsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .customers import (
    CustomersResource,
    AsyncCustomersResource,
    CustomersResourceWithRawResponse,
    AsyncCustomersResourceWithRawResponse,
    CustomersResourceWithStreamingResponse,
    AsyncCustomersResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .calculations import (
    CalculationsResource,
    AsyncCalculationsResource,
    CalculationsResourceWithRawResponse,
    AsyncCalculationsResourceWithRawResponse,
    CalculationsResourceWithStreamingResponse,
    AsyncCalculationsResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .refund_reversals import (
    RefundReversalsResource,
    AsyncRefundReversalsResource,
    RefundReversalsResourceWithRawResponse,
    AsyncRefundReversalsResourceWithRawResponse,
    RefundReversalsResourceWithStreamingResponse,
    AsyncRefundReversalsResourceWithStreamingResponse,
)
from ...types.tax_ping_response import TaxPingResponse
from .transactions.transactions import (
    TransactionsResource,
    AsyncTransactionsResource,
    TransactionsResourceWithRawResponse,
    AsyncTransactionsResourceWithRawResponse,
    TransactionsResourceWithStreamingResponse,
    AsyncTransactionsResourceWithStreamingResponse,
)

__all__ = ["TaxResource", "AsyncTaxResource"]


class TaxResource(SyncAPIResource):
    @cached_property
    def calculations(self) -> CalculationsResource:
        return CalculationsResource(self._client)

    @cached_property
    def transactions(self) -> TransactionsResource:
        return TransactionsResource(self._client)

    @cached_property
    def refunds(self) -> RefundsResource:
        return RefundsResource(self._client)

    @cached_property
    def refund_reversals(self) -> RefundReversalsResource:
        return RefundReversalsResource(self._client)

    @cached_property
    def products(self) -> ProductsResource:
        return ProductsResource(self._client)

    @cached_property
    def customers(self) -> CustomersResource:
        return CustomersResource(self._client)

    @cached_property
    def with_raw_response(self) -> TaxResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return TaxResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaxResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return TaxResourceWithStreamingResponse(self)

    def ping(
        self,
        *,
        x_api_version: Literal["2025-05-12", "2024-09-01"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaxPingResponse:
        """
        Authenticated health check endpoint that returns status, environment, timestamp,
        and API version

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given({"X-API-Version": str(x_api_version) if is_given(x_api_version) else not_given}),
            **(extra_headers or {}),
        }
        return self._get(
            "/tax/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaxPingResponse,
        )


class AsyncTaxResource(AsyncAPIResource):
    @cached_property
    def calculations(self) -> AsyncCalculationsResource:
        return AsyncCalculationsResource(self._client)

    @cached_property
    def transactions(self) -> AsyncTransactionsResource:
        return AsyncTransactionsResource(self._client)

    @cached_property
    def refunds(self) -> AsyncRefundsResource:
        return AsyncRefundsResource(self._client)

    @cached_property
    def refund_reversals(self) -> AsyncRefundReversalsResource:
        return AsyncRefundReversalsResource(self._client)

    @cached_property
    def products(self) -> AsyncProductsResource:
        return AsyncProductsResource(self._client)

    @cached_property
    def customers(self) -> AsyncCustomersResource:
        return AsyncCustomersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTaxResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTaxResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaxResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return AsyncTaxResourceWithStreamingResponse(self)

    async def ping(
        self,
        *,
        x_api_version: Literal["2025-05-12", "2024-09-01"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaxPingResponse:
        """
        Authenticated health check endpoint that returns status, environment, timestamp,
        and API version

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given({"X-API-Version": str(x_api_version) if is_given(x_api_version) else not_given}),
            **(extra_headers or {}),
        }
        return await self._get(
            "/tax/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaxPingResponse,
        )


class TaxResourceWithRawResponse:
    def __init__(self, tax: TaxResource) -> None:
        self._tax = tax

        self.ping = to_raw_response_wrapper(
            tax.ping,
        )

    @cached_property
    def calculations(self) -> CalculationsResourceWithRawResponse:
        return CalculationsResourceWithRawResponse(self._tax.calculations)

    @cached_property
    def transactions(self) -> TransactionsResourceWithRawResponse:
        return TransactionsResourceWithRawResponse(self._tax.transactions)

    @cached_property
    def refunds(self) -> RefundsResourceWithRawResponse:
        return RefundsResourceWithRawResponse(self._tax.refunds)

    @cached_property
    def refund_reversals(self) -> RefundReversalsResourceWithRawResponse:
        return RefundReversalsResourceWithRawResponse(self._tax.refund_reversals)

    @cached_property
    def products(self) -> ProductsResourceWithRawResponse:
        return ProductsResourceWithRawResponse(self._tax.products)

    @cached_property
    def customers(self) -> CustomersResourceWithRawResponse:
        return CustomersResourceWithRawResponse(self._tax.customers)


class AsyncTaxResourceWithRawResponse:
    def __init__(self, tax: AsyncTaxResource) -> None:
        self._tax = tax

        self.ping = async_to_raw_response_wrapper(
            tax.ping,
        )

    @cached_property
    def calculations(self) -> AsyncCalculationsResourceWithRawResponse:
        return AsyncCalculationsResourceWithRawResponse(self._tax.calculations)

    @cached_property
    def transactions(self) -> AsyncTransactionsResourceWithRawResponse:
        return AsyncTransactionsResourceWithRawResponse(self._tax.transactions)

    @cached_property
    def refunds(self) -> AsyncRefundsResourceWithRawResponse:
        return AsyncRefundsResourceWithRawResponse(self._tax.refunds)

    @cached_property
    def refund_reversals(self) -> AsyncRefundReversalsResourceWithRawResponse:
        return AsyncRefundReversalsResourceWithRawResponse(self._tax.refund_reversals)

    @cached_property
    def products(self) -> AsyncProductsResourceWithRawResponse:
        return AsyncProductsResourceWithRawResponse(self._tax.products)

    @cached_property
    def customers(self) -> AsyncCustomersResourceWithRawResponse:
        return AsyncCustomersResourceWithRawResponse(self._tax.customers)


class TaxResourceWithStreamingResponse:
    def __init__(self, tax: TaxResource) -> None:
        self._tax = tax

        self.ping = to_streamed_response_wrapper(
            tax.ping,
        )

    @cached_property
    def calculations(self) -> CalculationsResourceWithStreamingResponse:
        return CalculationsResourceWithStreamingResponse(self._tax.calculations)

    @cached_property
    def transactions(self) -> TransactionsResourceWithStreamingResponse:
        return TransactionsResourceWithStreamingResponse(self._tax.transactions)

    @cached_property
    def refunds(self) -> RefundsResourceWithStreamingResponse:
        return RefundsResourceWithStreamingResponse(self._tax.refunds)

    @cached_property
    def refund_reversals(self) -> RefundReversalsResourceWithStreamingResponse:
        return RefundReversalsResourceWithStreamingResponse(self._tax.refund_reversals)

    @cached_property
    def products(self) -> ProductsResourceWithStreamingResponse:
        return ProductsResourceWithStreamingResponse(self._tax.products)

    @cached_property
    def customers(self) -> CustomersResourceWithStreamingResponse:
        return CustomersResourceWithStreamingResponse(self._tax.customers)


class AsyncTaxResourceWithStreamingResponse:
    def __init__(self, tax: AsyncTaxResource) -> None:
        self._tax = tax

        self.ping = async_to_streamed_response_wrapper(
            tax.ping,
        )

    @cached_property
    def calculations(self) -> AsyncCalculationsResourceWithStreamingResponse:
        return AsyncCalculationsResourceWithStreamingResponse(self._tax.calculations)

    @cached_property
    def transactions(self) -> AsyncTransactionsResourceWithStreamingResponse:
        return AsyncTransactionsResourceWithStreamingResponse(self._tax.transactions)

    @cached_property
    def refunds(self) -> AsyncRefundsResourceWithStreamingResponse:
        return AsyncRefundsResourceWithStreamingResponse(self._tax.refunds)

    @cached_property
    def refund_reversals(self) -> AsyncRefundReversalsResourceWithStreamingResponse:
        return AsyncRefundReversalsResourceWithStreamingResponse(self._tax.refund_reversals)

    @cached_property
    def products(self) -> AsyncProductsResourceWithStreamingResponse:
        return AsyncProductsResourceWithStreamingResponse(self._tax.products)

    @cached_property
    def customers(self) -> AsyncCustomersResourceWithStreamingResponse:
        return AsyncCustomersResourceWithStreamingResponse(self._tax.customers)
