# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.tax import refund_create_params
from ..._base_client import make_request_options
from ...types.shared.refund_response import RefundResponse

__all__ = ["RefundsResource", "AsyncRefundsResource"]


class RefundsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RefundsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return RefundsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RefundsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return RefundsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        transaction_id: str,
        type: str,
        line_items: Iterable[refund_create_params.LineItem] | Omit = omit,
        refund_processed_at: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RefundResponse:
        """
        Add a refund to a transaction

        Args:
          transaction_id: The ID of the `transaction` to refund. This is the `transaction_id` returned
              from the `/transactions` creation response.

          type: This will be either `'full'` or `'partial'`. If `type='partial'`, you must also
              provide the line item(s) you wish to apply refunds against.

          line_items: If the refund is `type=full`, line items aren't necessary. If the refund is
              `type=partial`, you must provide the line item(s) you wish to apply refunds
              against using a `reference_product_id`.

          refund_processed_at: Unix timestamp in **seconds** representing the date and time the refund was
              made. If not provided, the current date and time will be used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/tax/refunds",
            body=maybe_transform(
                {
                    "transaction_id": transaction_id,
                    "type": type,
                    "line_items": line_items,
                    "refund_processed_at": refund_processed_at,
                },
                refund_create_params.RefundCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RefundResponse,
        )


class AsyncRefundsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRefundsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRefundsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRefundsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return AsyncRefundsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        transaction_id: str,
        type: str,
        line_items: Iterable[refund_create_params.LineItem] | Omit = omit,
        refund_processed_at: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RefundResponse:
        """
        Add a refund to a transaction

        Args:
          transaction_id: The ID of the `transaction` to refund. This is the `transaction_id` returned
              from the `/transactions` creation response.

          type: This will be either `'full'` or `'partial'`. If `type='partial'`, you must also
              provide the line item(s) you wish to apply refunds against.

          line_items: If the refund is `type=full`, line items aren't necessary. If the refund is
              `type=partial`, you must provide the line item(s) you wish to apply refunds
              against using a `reference_product_id`.

          refund_processed_at: Unix timestamp in **seconds** representing the date and time the refund was
              made. If not provided, the current date and time will be used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/tax/refunds",
            body=await async_maybe_transform(
                {
                    "transaction_id": transaction_id,
                    "type": type,
                    "line_items": line_items,
                    "refund_processed_at": refund_processed_at,
                },
                refund_create_params.RefundCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RefundResponse,
        )


class RefundsResourceWithRawResponse:
    def __init__(self, refunds: RefundsResource) -> None:
        self._refunds = refunds

        self.create = to_raw_response_wrapper(
            refunds.create,
        )


class AsyncRefundsResourceWithRawResponse:
    def __init__(self, refunds: AsyncRefundsResource) -> None:
        self._refunds = refunds

        self.create = async_to_raw_response_wrapper(
            refunds.create,
        )


class RefundsResourceWithStreamingResponse:
    def __init__(self, refunds: RefundsResource) -> None:
        self._refunds = refunds

        self.create = to_streamed_response_wrapper(
            refunds.create,
        )


class AsyncRefundsResourceWithStreamingResponse:
    def __init__(self, refunds: AsyncRefundsResource) -> None:
        self._refunds = refunds

        self.create = async_to_streamed_response_wrapper(
            refunds.create,
        )
