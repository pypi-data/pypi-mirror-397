# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ...types.tax import refund_reversal_create_params
from ..._base_client import make_request_options
from ...types.shared.refund_response import RefundResponse

__all__ = ["RefundReversalsResource", "AsyncRefundReversalsResource"]


class RefundReversalsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RefundReversalsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return RefundReversalsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RefundReversalsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return RefundReversalsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        refund_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RefundResponse:
        """
        Reverse a refund you've previously created

        Args:
          refund_id: The ID of the refund to reverse

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/tax/refund_reversals",
            body=maybe_transform({"refund_id": refund_id}, refund_reversal_create_params.RefundReversalCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RefundResponse,
        )


class AsyncRefundReversalsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRefundReversalsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRefundReversalsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRefundReversalsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return AsyncRefundReversalsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        refund_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RefundResponse:
        """
        Reverse a refund you've previously created

        Args:
          refund_id: The ID of the refund to reverse

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/tax/refund_reversals",
            body=await async_maybe_transform(
                {"refund_id": refund_id}, refund_reversal_create_params.RefundReversalCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RefundResponse,
        )


class RefundReversalsResourceWithRawResponse:
    def __init__(self, refund_reversals: RefundReversalsResource) -> None:
        self._refund_reversals = refund_reversals

        self.create = to_raw_response_wrapper(
            refund_reversals.create,
        )


class AsyncRefundReversalsResourceWithRawResponse:
    def __init__(self, refund_reversals: AsyncRefundReversalsResource) -> None:
        self._refund_reversals = refund_reversals

        self.create = async_to_raw_response_wrapper(
            refund_reversals.create,
        )


class RefundReversalsResourceWithStreamingResponse:
    def __init__(self, refund_reversals: RefundReversalsResource) -> None:
        self._refund_reversals = refund_reversals

        self.create = to_streamed_response_wrapper(
            refund_reversals.create,
        )


class AsyncRefundReversalsResourceWithStreamingResponse:
    def __init__(self, refund_reversals: AsyncRefundReversalsResource) -> None:
        self._refund_reversals = refund_reversals

        self.create = async_to_streamed_response_wrapper(
            refund_reversals.create,
        )
