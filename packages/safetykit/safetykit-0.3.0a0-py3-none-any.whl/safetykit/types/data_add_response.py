# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DataAddResponse"]


class DataAddResponse(BaseModel):
    """Response confirming data was accepted for asynchronous processing.

    The requestId can be used for debugging and tracking.
    """

    request_id: str = FieldInfo(alias="requestId")
    """Unique identifier for tracking this request.

    Data processing happens asynchronously after this response.
    """

    status: Literal["accepted"]
    """Request was accepted for processing"""
