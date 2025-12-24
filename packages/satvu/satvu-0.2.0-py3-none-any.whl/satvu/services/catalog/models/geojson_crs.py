from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, Field


class GeojsonCRS(BaseModel):
    """
    Attributes:
        properties (Union[None, dict]):
        type_ (Union[None, str]):
    """

    properties: Union[None, dict] = Field(
        default=None, description=None, alias="properties"
    )
    type_: Union[None, str] = Field(default=None, description=None, alias="type")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
