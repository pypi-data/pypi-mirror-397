# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["DecisionCreateParams"]


class DecisionCreateParams(TypedDict, total=False):
    content: Required[Dict[str, Union[str, float, bool, SequenceNotStr[str], None]]]
    """The data to be reviewed. The structure depends on the type of content."""

    type: Required[str]
    """The type of content to review"""

    metadata: Dict[str, Union[str, float, bool, None]]
    """Customer metadata as key-value pairs"""
