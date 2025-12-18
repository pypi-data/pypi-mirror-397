# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .observation import Observation

__all__ = ["PageObservation"]


class PageObservation(BaseModel):
    items: List[Observation]

    page: int

    size: int

    pages: Optional[int] = None

    total: Optional[int] = None
