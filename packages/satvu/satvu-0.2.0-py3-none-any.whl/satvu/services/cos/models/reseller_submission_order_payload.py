from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResellerSubmissionOrderPayload(BaseModel):
    """Order payload for resellers

    Attributes:
        reseller_end_user_id (UUID): The ID of the end user for whom the order is placed for.
        item_id (list[str] | str): The item ID.
        licence_level (str): The licence level for the order. Licence levels are specific to the contract.
        name (None | str): The optional name of the order
    """

    reseller_end_user_id: UUID = Field(
        ...,
        description="""The ID of the end user for whom the order is placed for.""",
        alias="reseller_end_user_id",
    )
    item_id: list[str] | str = Field(
        ..., description="""The item ID.""", alias="item_id"
    )
    licence_level: str = Field(
        ...,
        description="""The licence level for the order. Licence levels are specific to the contract.""",
        alias="licence_level",
    )
    name: None | str = Field(
        default=None, description="""The optional name of the order""", alias="name"
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
