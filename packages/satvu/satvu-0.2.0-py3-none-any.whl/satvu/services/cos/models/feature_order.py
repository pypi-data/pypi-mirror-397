from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ..models.order import Order
    from ..models.point_geometry import PointGeometry
    from ..models.polygon_geometry import PolygonGeometry


class FeatureOrder(BaseModel):
    """
    Attributes:
        id (str | UUID): The unique identifier of the item within the order.
        properties (Order):
        type_ (Union[Literal['Feature'], None]):  Default: 'Feature'.
        geometry (Union['PointGeometry', 'PolygonGeometry', None]): Defines the full footprint of the asset represented
            by the item.
    """

    id: str | UUID = Field(
        ...,
        description="""The unique identifier of the item within the order.""",
        alias="id",
    )
    properties: Order = Field(..., description=None, alias="properties")
    type_: Union[Literal["Feature"], None] = Field(
        default="Feature", description=None, alias="type"
    )
    geometry: Union[PointGeometry, PolygonGeometry, None] = Field(
        default=None,
        description="""Defines the full footprint of the asset represented by the item.""",
        alias="geometry",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
