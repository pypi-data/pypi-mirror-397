from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrderItemPrice(BaseModel):
    """
    Attributes:
        item_price (int): The price of the image in minor units of the currency e.g. pence, cents.
        currency (str): The currency of the order.
    """

    item_price: int = Field(
        ...,
        description="""The price of the image in minor units of the currency e.g. pence, cents.""",
        alias="item_price",
    )
    currency: str = Field(
        ..., description="""The currency of the order.""", alias="currency"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
