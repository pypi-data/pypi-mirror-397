# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from safetykit import Safetykit, AsyncSafetykit
from tests.utils import assert_matches_type
from safetykit.types import BatchGetResponse, BatchCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatches:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Safetykit) -> None:
        batch = client.batches.create(
            type="product_review",
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Safetykit) -> None:
        response = client.batches.with_raw_response.create(
            type="product_review",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Safetykit) -> None:
        with client.batches.with_streaming_response.create(
            type="product_review",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(BatchCreateResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Safetykit) -> None:
        batch = client.batches.get(
            "batch_id",
        )
        assert_matches_type(BatchGetResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Safetykit) -> None:
        response = client.batches.with_raw_response.get(
            "batch_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(BatchGetResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Safetykit) -> None:
        with client.batches.with_streaming_response.get(
            "batch_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(BatchGetResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Safetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.batches.with_raw_response.get(
                "",
            )


class TestAsyncBatches:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSafetykit) -> None:
        batch = await async_client.batches.create(
            type="product_review",
        )
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSafetykit) -> None:
        response = await async_client.batches.with_raw_response.create(
            type="product_review",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(BatchCreateResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSafetykit) -> None:
        async with async_client.batches.with_streaming_response.create(
            type="product_review",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(BatchCreateResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncSafetykit) -> None:
        batch = await async_client.batches.get(
            "batch_id",
        )
        assert_matches_type(BatchGetResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSafetykit) -> None:
        response = await async_client.batches.with_raw_response.get(
            "batch_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(BatchGetResponse, batch, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSafetykit) -> None:
        async with async_client.batches.with_streaming_response.get(
            "batch_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(BatchGetResponse, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSafetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.batches.with_raw_response.get(
                "",
            )
