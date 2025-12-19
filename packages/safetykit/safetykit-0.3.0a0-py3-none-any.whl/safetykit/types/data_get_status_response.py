# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DataGetStatusResponse"]


class DataGetStatusResponse(BaseModel):
    """Response containing the status and progress of an add request."""

    created_at: str = FieldInfo(alias="createdAt")
    """ISO timestamp when the request was created"""

    object_count: float = FieldInfo(alias="objectCount")
    """Number of objects in the request"""

    status: Literal["UPLOADING", "INGESTING", "COMPLETE"]
    """Current processing status of the add request"""
