from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BatchBalanceResponse(BaseModel):
    """
    Attributes:
        balances (dict): Mapping of contract IDs to their credit balance responses
    """

    balances: dict = Field(
        ...,
        description="""Mapping of contract IDs to their credit balance responses""",
        alias="balances",
    )

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
