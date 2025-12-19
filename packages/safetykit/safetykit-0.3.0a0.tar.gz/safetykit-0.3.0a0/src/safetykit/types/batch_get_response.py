# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["BatchGetResponse"]


class BatchGetResponse(BaseModel):
    """Batch status and progress information"""

    batch_count: int
    """Total number of decisions in the batch"""

    batch_id: str
    """Unique identifier for the batch"""

    batch_status: Literal["WAITING_FOR_UPLOAD", "PENDING", "SUCCESS", "ERROR", "CANCELLED"]
    """Status of the batch"""

    cancelled_count: int
    """Number of decisions that were cancelled"""

    download_url: Optional[str] = None
    """URL to download results when complete"""

    error_count: int
    """Number of decisions that failed"""

    pending_count: int
    """Number of decisions in progress"""

    success_count: int
    """Number of decisions successfully completed"""

    upload_url: Optional[str] = None
    """Upload URL (null after batch is created)"""

    policy_id: Optional[str] = None
    """Policy ID applied to batch items"""

    policy_version: Optional[str] = None
    """Policy version applied to batch items"""
