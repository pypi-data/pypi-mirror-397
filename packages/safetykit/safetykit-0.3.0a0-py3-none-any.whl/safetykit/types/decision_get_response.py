# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DecisionGetResponse", "Label"]


class Label(BaseModel):
    applied: bool
    """Whether or not the label was applied in this decision"""

    explanation: str
    """An explanation of why the label was applied or not applied"""

    name: str
    """The name of the label"""


class DecisionGetResponse(BaseModel):
    """Decision result data"""

    decision_id: str
    """Unique identifier for the decision"""

    decision_status: Literal["SUCCESS", "PENDING", "ERROR", "CANCELLED"]
    """Status of the decision"""

    labels: Optional[List[Label]] = None
    """Labels assigned during the decision process"""

    metadata: Dict[str, Union[str, float, bool, None]]
    """Customer metadata as key-value pairs"""

    result: Optional[str] = None
    """The result of the policy (possible values are determined by the policy)"""

    policy_id: Optional[str] = None
    """Policy ID used for this decision"""

    policy_version: Optional[str] = None
    """Policy version used for this decision"""
