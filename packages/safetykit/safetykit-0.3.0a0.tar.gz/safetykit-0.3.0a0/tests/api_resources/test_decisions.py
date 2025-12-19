# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from safetykit import Safetykit, AsyncSafetykit
from tests.utils import assert_matches_type
from safetykit.types import DecisionGetResponse, DecisionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDecisions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Safetykit) -> None:
        decision = client.decisions.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
        )
        assert_matches_type(DecisionCreateResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Safetykit) -> None:
        decision = client.decisions.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
            metadata={
                "user_id": "user-456",
                "batch_name": "Daily review",
            },
        )
        assert_matches_type(DecisionCreateResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Safetykit) -> None:
        response = client.decisions.with_raw_response.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        decision = response.parse()
        assert_matches_type(DecisionCreateResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Safetykit) -> None:
        with client.decisions.with_streaming_response.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            decision = response.parse()
            assert_matches_type(DecisionCreateResponse, decision, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Safetykit) -> None:
        decision = client.decisions.get(
            "decision_id",
        )
        assert_matches_type(DecisionGetResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Safetykit) -> None:
        response = client.decisions.with_raw_response.get(
            "decision_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        decision = response.parse()
        assert_matches_type(DecisionGetResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Safetykit) -> None:
        with client.decisions.with_streaming_response.get(
            "decision_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            decision = response.parse()
            assert_matches_type(DecisionGetResponse, decision, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Safetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `decision_id` but received ''"):
            client.decisions.with_raw_response.get(
                "",
            )


class TestAsyncDecisions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSafetykit) -> None:
        decision = await async_client.decisions.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
        )
        assert_matches_type(DecisionCreateResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSafetykit) -> None:
        decision = await async_client.decisions.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
            metadata={
                "user_id": "user-456",
                "batch_name": "Daily review",
            },
        )
        assert_matches_type(DecisionCreateResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSafetykit) -> None:
        response = await async_client.decisions.with_raw_response.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        decision = await response.parse()
        assert_matches_type(DecisionCreateResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSafetykit) -> None:
        async with async_client.decisions.with_streaming_response.create(
            content={"url": "https://www.example.com/products/42"},
            type="product_review",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            decision = await response.parse()
            assert_matches_type(DecisionCreateResponse, decision, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncSafetykit) -> None:
        decision = await async_client.decisions.get(
            "decision_id",
        )
        assert_matches_type(DecisionGetResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSafetykit) -> None:
        response = await async_client.decisions.with_raw_response.get(
            "decision_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        decision = await response.parse()
        assert_matches_type(DecisionGetResponse, decision, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSafetykit) -> None:
        async with async_client.decisions.with_streaming_response.get(
            "decision_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            decision = await response.parse()
            assert_matches_type(DecisionGetResponse, decision, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSafetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `decision_id` but received ''"):
            await async_client.decisions.with_raw_response.get(
                "",
            )
