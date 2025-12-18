# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DatasetGetResponse", "Label", "Snapshot"]


class Label(BaseModel):
    id: str

    description: Optional[str] = None

    name: str


class Snapshot(BaseModel):
    id: str

    created_at: str


class DatasetGetResponse(BaseModel):
    id: str

    created_at: str

    datapoints_count: int

    labels: List[Label]
    """List of labels associated with the dataset"""

    name: str

    project_id: Optional[str] = None

    snapshots: List[Snapshot]
    """List of snapshots associated with the dataset"""

    status: Literal["processing", "completed", "failed"]

    updated_at: str
