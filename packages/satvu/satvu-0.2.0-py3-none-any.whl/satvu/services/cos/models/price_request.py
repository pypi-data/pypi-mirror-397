from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PriceRequest(BaseModel):
    """Request payload for submitting an order.

    Attributes:
        item_id (list[str] | str): The item ID.
        name (None | str): The optional name of the order
        licence_level (None | str): The licence level for the order. Licence levels are specific to the contract. Must
            be provided unless the `baseprice` query parameter is set to true.
    """

    item_id: list[str] | str = Field(
        ..., description="""The item ID.""", alias="item_id"
    )
    name: None | str = Field(
        default=None, description="""The optional name of the order""", alias="name"
    )
    licence_level: None | str = Field(
        default=None,
        description="""The licence level for the order. Licence levels are specific to the contract. Must be provided unless the `baseprice` query parameter is set to true.""",
        alias="licence_level",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
