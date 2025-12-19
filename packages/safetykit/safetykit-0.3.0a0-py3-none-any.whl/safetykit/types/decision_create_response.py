# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union

from .._models import BaseModel

__all__ = ["DecisionCreateResponse"]


class DecisionCreateResponse(BaseModel):
    """Response containing the decision ID"""

    decision_id: str
    """Unique identifier for the decision"""

    metadata: Dict[str, Union[str, float, bool, None]]
    """Customer metadata as key-value pairs"""

    type: str
    """Type of content to review"""
