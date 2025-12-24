from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ..models.direction import Direction
from ..models.sortable_field import SortableField


class SortEntities(BaseModel):
    """
    Attributes:
        field ('SortableField'):
        direction ('Direction'): The directionality of the sort.
    """

    field: SortableField = Field(..., description=None, alias="field")
    direction: Direction = Field(
        ..., description="""The directionality of the sort.""", alias="direction"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
