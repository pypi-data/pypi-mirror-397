# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union

import httpx

from ..types import decision_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.decision_get_response import DecisionGetResponse
from ..types.decision_create_response import DecisionCreateResponse

__all__ = ["DecisionsResource", "AsyncDecisionsResource"]


class DecisionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DecisionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GetSafetyKit/safetykit-python#accessing-raw-response-data-eg-headers
        """
        return DecisionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DecisionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GetSafetyKit/safetykit-python#with_streaming_response
        """
        return DecisionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        content: Dict[str, Union[str, float, bool, SequenceNotStr[str], None]],
        type: str,
        metadata: Dict[str, Union[str, float, bool, None]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DecisionCreateResponse:
        """Submit content for review and receive a decision ID to track the results.

        The
        decision is processed asynchronously.

        Args:
          content: The data to be reviewed. The structure depends on the type of content.

          type: The type of content to review

          metadata: Customer metadata as key-value pairs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/decisions",
            body=maybe_transform(
                {
                    "content": content,
                    "type": type,
                    "metadata": metadata,
                },
                decision_create_params.DecisionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DecisionCreateResponse,
        )

    def get(
        self,
        decision_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DecisionGetResponse:
        """
        Retrieve the results of a previously submitted decision by its ID.

        Args:
          decision_id: The decision ID to retrieve

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not decision_id:
            raise ValueError(f"Expected a non-empty value for `decision_id` but received {decision_id!r}")
        return self._get(
            f"/v1/decisions/{decision_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DecisionGetResponse,
        )


class AsyncDecisionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDecisionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GetSafetyKit/safetykit-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDecisionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDecisionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GetSafetyKit/safetykit-python#with_streaming_response
        """
        return AsyncDecisionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        content: Dict[str, Union[str, float, bool, SequenceNotStr[str], None]],
        type: str,
        metadata: Dict[str, Union[str, float, bool, None]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DecisionCreateResponse:
        """Submit content for review and receive a decision ID to track the results.

        The
        decision is processed asynchronously.

        Args:
          content: The data to be reviewed. The structure depends on the type of content.

          type: The type of content to review

          metadata: Customer metadata as key-value pairs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/decisions",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "type": type,
                    "metadata": metadata,
                },
                decision_create_params.DecisionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DecisionCreateResponse,
        )

    async def get(
        self,
        decision_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DecisionGetResponse:
        """
        Retrieve the results of a previously submitted decision by its ID.

        Args:
          decision_id: The decision ID to retrieve

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not decision_id:
            raise ValueError(f"Expected a non-empty value for `decision_id` but received {decision_id!r}")
        return await self._get(
            f"/v1/decisions/{decision_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DecisionGetResponse,
        )


class DecisionsResourceWithRawResponse:
    def __init__(self, decisions: DecisionsResource) -> None:
        self._decisions = decisions

        self.create = to_raw_response_wrapper(
            decisions.create,
        )
        self.get = to_raw_response_wrapper(
            decisions.get,
        )


class AsyncDecisionsResourceWithRawResponse:
    def __init__(self, decisions: AsyncDecisionsResource) -> None:
        self._decisions = decisions

        self.create = async_to_raw_response_wrapper(
            decisions.create,
        )
        self.get = async_to_raw_response_wrapper(
            decisions.get,
        )


class DecisionsResourceWithStreamingResponse:
    def __init__(self, decisions: DecisionsResource) -> None:
        self._decisions = decisions

        self.create = to_streamed_response_wrapper(
            decisions.create,
        )
        self.get = to_streamed_response_wrapper(
            decisions.get,
        )


class AsyncDecisionsResourceWithStreamingResponse:
    def __init__(self, decisions: AsyncDecisionsResource) -> None:
        self._decisions = decisions

        self.create = async_to_streamed_response_wrapper(
            decisions.create,
        )
        self.get = async_to_streamed_response_wrapper(
            decisions.get,
        )
