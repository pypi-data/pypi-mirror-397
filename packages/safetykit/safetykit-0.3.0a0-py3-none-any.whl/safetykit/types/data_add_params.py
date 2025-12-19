# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DataAddParams", "Data", "Schema", "SchemaDisplayHint"]


class DataAddParams(TypedDict, total=False):
    data: Iterable[Data]

    schema: Dict[str, Schema]
    """Schema mapping field names to their definitions.

    Use content_type to specify which fields contain URLs that should be processed
    (images, videos, or websites). Use display_hint to provide UI rendering hints.
    """


class Data(TypedDict, total=False):
    """A data object to ingest.

    Must have an id field. All other fields are flexible and can any JSON types.
    """

    id: Required[str]
    """
    Unique identifier for this data object. This should be a meaningful identifier
    in the customer's system, as it is the main way to search for specific items
    between systems.
    """

    customer_metadata: Dict[str, Optional[object]]
    """
    Customer metadata that is not be to part of the review, used to passthrough data
    to the response API.
    """


class SchemaDisplayHint(TypedDict, total=False):
    """Display hint for UI rendering of this field"""

    type: Required[
        Literal[
            "title",
            "subtitle",
            "description",
            "primary_image_url",
            "location",
            "date",
            "email.replyTo",
            "email.body",
            "email.subject",
        ]
    ]
    """The display hint type"""


class Schema(TypedDict, total=False):
    """Schema definition for a data field"""

    content_type: Literal["image_url", "video_url", "website_url"]
    """The type of content (image_url, video_url, or website_url).

    When specified, SafetyKit will process the URL.
    """

    display_hint: SchemaDisplayHint
    """Display hint for UI rendering of this field"""

    namespace_ref: str
    """
    The namespace which an id refers to, creating a parent-child relationship with
    that namespace.
    """
