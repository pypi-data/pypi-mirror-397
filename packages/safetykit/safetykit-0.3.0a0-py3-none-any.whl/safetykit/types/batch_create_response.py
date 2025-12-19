# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["BatchCreateResponse"]


class BatchCreateResponse(BaseModel):
    """Response containing batch ID and upload URL"""

    batch_id: str
    """Unique identifier for the batch"""

    batch_status: Literal["WAITING_FOR_UPLOAD", "PENDING", "SUCCESS", "ERROR", "CANCELLED"]
    """Status of the batch"""

    download_url: Optional[str] = None
    """Download URL (null until batch is complete)"""

    upload_url: str
    """Presigned S3 URL for uploading the batch CSV file"""
