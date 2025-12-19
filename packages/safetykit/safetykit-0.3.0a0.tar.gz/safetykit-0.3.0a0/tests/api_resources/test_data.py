# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from safetykit import Safetykit, AsyncSafetykit
from tests.utils import assert_matches_type
from safetykit.types import DataAddResponse, DataGetStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestData:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_add(self, client: Safetykit) -> None:
        data = client.data.add(
            namespace="namespace",
        )
        assert_matches_type(DataAddResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_add_with_all_params(self, client: Safetykit) -> None:
        data = client.data.add(
            namespace="namespace",
            data=[
                {
                    "id": "user-12345",
                    "customer_metadata": {"foo": "bar"},
                }
            ],
            schema={
                "profile_image": {
                    "content_type": "image_url",
                    "display_hint": {"type": "title"},
                    "namespace_ref": "namespace_ref",
                },
                "cover_photo": {
                    "content_type": "image_url",
                    "display_hint": {"type": "title"},
                    "namespace_ref": "namespace_ref",
                },
                "website": {
                    "content_type": "website_url",
                    "display_hint": {"type": "title"},
                    "namespace_ref": "namespace_ref",
                },
            },
        )
        assert_matches_type(DataAddResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_add(self, client: Safetykit) -> None:
        response = client.data.with_raw_response.add(
            namespace="namespace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data = response.parse()
        assert_matches_type(DataAddResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_add(self, client: Safetykit) -> None:
        with client.data.with_streaming_response.add(
            namespace="namespace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data = response.parse()
            assert_matches_type(DataAddResponse, data, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_add(self, client: Safetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `namespace` but received ''"):
            client.data.with_raw_response.add(
                namespace="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_status(self, client: Safetykit) -> None:
        data = client.data.get_status(
            "requestId",
        )
        assert_matches_type(DataGetStatusResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_status(self, client: Safetykit) -> None:
        response = client.data.with_raw_response.get_status(
            "requestId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data = response.parse()
        assert_matches_type(DataGetStatusResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_status(self, client: Safetykit) -> None:
        with client.data.with_streaming_response.get_status(
            "requestId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data = response.parse()
            assert_matches_type(DataGetStatusResponse, data, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_status(self, client: Safetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `request_id` but received ''"):
            client.data.with_raw_response.get_status(
                "",
            )


class TestAsyncData:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_add(self, async_client: AsyncSafetykit) -> None:
        data = await async_client.data.add(
            namespace="namespace",
        )
        assert_matches_type(DataAddResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_add_with_all_params(self, async_client: AsyncSafetykit) -> None:
        data = await async_client.data.add(
            namespace="namespace",
            data=[
                {
                    "id": "user-12345",
                    "customer_metadata": {"foo": "bar"},
                }
            ],
            schema={
                "profile_image": {
                    "content_type": "image_url",
                    "display_hint": {"type": "title"},
                    "namespace_ref": "namespace_ref",
                },
                "cover_photo": {
                    "content_type": "image_url",
                    "display_hint": {"type": "title"},
                    "namespace_ref": "namespace_ref",
                },
                "website": {
                    "content_type": "website_url",
                    "display_hint": {"type": "title"},
                    "namespace_ref": "namespace_ref",
                },
            },
        )
        assert_matches_type(DataAddResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_add(self, async_client: AsyncSafetykit) -> None:
        response = await async_client.data.with_raw_response.add(
            namespace="namespace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data = await response.parse()
        assert_matches_type(DataAddResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncSafetykit) -> None:
        async with async_client.data.with_streaming_response.add(
            namespace="namespace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data = await response.parse()
            assert_matches_type(DataAddResponse, data, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_add(self, async_client: AsyncSafetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `namespace` but received ''"):
            await async_client.data.with_raw_response.add(
                namespace="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_status(self, async_client: AsyncSafetykit) -> None:
        data = await async_client.data.get_status(
            "requestId",
        )
        assert_matches_type(DataGetStatusResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncSafetykit) -> None:
        response = await async_client.data.with_raw_response.get_status(
            "requestId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data = await response.parse()
        assert_matches_type(DataGetStatusResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncSafetykit) -> None:
        async with async_client.data.with_streaming_response.get_status(
            "requestId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data = await response.parse()
            assert_matches_type(DataGetStatusResponse, data, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncSafetykit) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `request_id` but received ''"):
            await async_client.data.with_raw_response.get_status(
                "",
            )
