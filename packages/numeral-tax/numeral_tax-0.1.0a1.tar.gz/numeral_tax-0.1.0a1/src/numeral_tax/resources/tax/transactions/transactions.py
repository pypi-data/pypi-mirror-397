# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .refunds import (
    RefundsResource,
    AsyncRefundsResource,
    RefundsResourceWithRawResponse,
    AsyncRefundsResourceWithRawResponse,
    RefundsResourceWithStreamingResponse,
    AsyncRefundsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.tax import transaction_create_params
from ...._base_client import make_request_options
from ....types.metadata_param import MetadataParam
from ....types.tax.transaction_response import TransactionResponse
from ....types.tax.delete_transaction_response import DeleteTransactionResponse

__all__ = ["TransactionsResource", "AsyncTransactionsResource"]


class TransactionsResource(SyncAPIResource):
    @cached_property
    def refunds(self) -> RefundsResource:
        return RefundsResource(self._client)

    @cached_property
    def with_raw_response(self) -> TransactionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return TransactionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TransactionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return TransactionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        calculation_id: str,
        reference_order_id: str,
        metadata: MetadataParam | Omit = omit,
        transaction_processed_at: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TransactionResponse:
        """
        Record a completed sale

        Args:
          calculation_id: The ID of the `calculation` that you want to record as a sale

          reference_order_id: The ID of this order in your system. Must be unique among all your
              `transactions`

          metadata: You can store arbitrary keys and values in the metadata. Any valid JSON object
              whose values are less than 255 characters long is accepted.

          transaction_processed_at: Unix timestamp in **seconds** representing the date and time your sale was made.
              If not provided, the current date and time will be used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/tax/transactions",
            body=maybe_transform(
                {
                    "calculation_id": calculation_id,
                    "reference_order_id": reference_order_id,
                    "metadata": metadata,
                    "transaction_processed_at": transaction_processed_at,
                },
                transaction_create_params.TransactionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransactionResponse,
        )

    def retrieve(
        self,
        transaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TransactionResponse:
        """
        Retrieve the details of a specific transaction

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transaction_id:
            raise ValueError(f"Expected a non-empty value for `transaction_id` but received {transaction_id!r}")
        return self._get(
            f"/tax/transactions/{transaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransactionResponse,
        )

    def delete(
        self,
        transaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteTransactionResponse:
        """
        Delete a specific transaction using its ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transaction_id:
            raise ValueError(f"Expected a non-empty value for `transaction_id` but received {transaction_id!r}")
        return self._delete(
            f"/tax/transactions/{transaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteTransactionResponse,
        )


class AsyncTransactionsResource(AsyncAPIResource):
    @cached_property
    def refunds(self) -> AsyncRefundsResource:
        return AsyncRefundsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTransactionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTransactionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTransactionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/NumeralHQ/numeral-tax-python#with_streaming_response
        """
        return AsyncTransactionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        calculation_id: str,
        reference_order_id: str,
        metadata: MetadataParam | Omit = omit,
        transaction_processed_at: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TransactionResponse:
        """
        Record a completed sale

        Args:
          calculation_id: The ID of the `calculation` that you want to record as a sale

          reference_order_id: The ID of this order in your system. Must be unique among all your
              `transactions`

          metadata: You can store arbitrary keys and values in the metadata. Any valid JSON object
              whose values are less than 255 characters long is accepted.

          transaction_processed_at: Unix timestamp in **seconds** representing the date and time your sale was made.
              If not provided, the current date and time will be used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/tax/transactions",
            body=await async_maybe_transform(
                {
                    "calculation_id": calculation_id,
                    "reference_order_id": reference_order_id,
                    "metadata": metadata,
                    "transaction_processed_at": transaction_processed_at,
                },
                transaction_create_params.TransactionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransactionResponse,
        )

    async def retrieve(
        self,
        transaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TransactionResponse:
        """
        Retrieve the details of a specific transaction

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transaction_id:
            raise ValueError(f"Expected a non-empty value for `transaction_id` but received {transaction_id!r}")
        return await self._get(
            f"/tax/transactions/{transaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransactionResponse,
        )

    async def delete(
        self,
        transaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeleteTransactionResponse:
        """
        Delete a specific transaction using its ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transaction_id:
            raise ValueError(f"Expected a non-empty value for `transaction_id` but received {transaction_id!r}")
        return await self._delete(
            f"/tax/transactions/{transaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteTransactionResponse,
        )


class TransactionsResourceWithRawResponse:
    def __init__(self, transactions: TransactionsResource) -> None:
        self._transactions = transactions

        self.create = to_raw_response_wrapper(
            transactions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            transactions.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            transactions.delete,
        )

    @cached_property
    def refunds(self) -> RefundsResourceWithRawResponse:
        return RefundsResourceWithRawResponse(self._transactions.refunds)


class AsyncTransactionsResourceWithRawResponse:
    def __init__(self, transactions: AsyncTransactionsResource) -> None:
        self._transactions = transactions

        self.create = async_to_raw_response_wrapper(
            transactions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            transactions.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            transactions.delete,
        )

    @cached_property
    def refunds(self) -> AsyncRefundsResourceWithRawResponse:
        return AsyncRefundsResourceWithRawResponse(self._transactions.refunds)


class TransactionsResourceWithStreamingResponse:
    def __init__(self, transactions: TransactionsResource) -> None:
        self._transactions = transactions

        self.create = to_streamed_response_wrapper(
            transactions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            transactions.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            transactions.delete,
        )

    @cached_property
    def refunds(self) -> RefundsResourceWithStreamingResponse:
        return RefundsResourceWithStreamingResponse(self._transactions.refunds)


class AsyncTransactionsResourceWithStreamingResponse:
    def __init__(self, transactions: AsyncTransactionsResource) -> None:
        self._transactions = transactions

        self.create = async_to_streamed_response_wrapper(
            transactions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            transactions.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            transactions.delete,
        )

    @cached_property
    def refunds(self) -> AsyncRefundsResourceWithStreamingResponse:
        return AsyncRefundsResourceWithStreamingResponse(self._transactions.refunds)
