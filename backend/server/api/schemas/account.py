"""Pydantic schemas for Account API."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from server.models.account import AccountType, Currency, EconomicArea


class AccountBase(BaseModel):
    """Base schema for Account with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Account name")
    institution: str = Field(
        ..., min_length=1, max_length=255, description="Financial institution name"
    )
    currency: str = Field(..., description="ISO 4217 currency code")
    account_type: str = Field(..., description="Account type")
    economic_area: Optional[str] = Field(
        None, description="Economic area classification"
    )
    datelock_from: Optional[date] = Field(
        None, description="Date lock for ingestion (nullable)"
    )


class AccountCreate(AccountBase):
    """Schema for creating a new account."""

    pass


class AccountUpdate(BaseModel):
    """Schema for updating an account (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    institution: Optional[str] = Field(None, min_length=1, max_length=255)
    currency: Optional[str] = None
    account_type: Optional[str] = None
    economic_area: Optional[str] = None
    datelock_from: Optional[date] = None


class AccountResponse(AccountBase):
    """Schema for account response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def map_type_to_account_type(cls, data):
        """Map 'type' field from model to 'account_type' in response."""
        if hasattr(data, "__dict__"):
            # It's an ORM object
            obj_dict = {}
            for key, value in data.__dict__.items():
                if key == "type":
                    obj_dict["account_type"] = (
                        value.value if hasattr(value, "value") else str(value)
                    )
                elif key == "currency":
                    obj_dict["currency"] = (
                        value.value if hasattr(value, "value") else str(value)
                    )
                elif key == "economic_area":
                    obj_dict["economic_area"] = (
                        value.value
                        if value and hasattr(value, "value")
                        else (str(value) if value else None)
                    )
                else:
                    obj_dict[key] = value
            return obj_dict
        elif isinstance(data, dict) and "type" in data:
            # It's a dict with 'type' key
            data["account_type"] = data.pop("type")
        return data


class AccountTypeOption(BaseModel):
    """Schema for account type option in meta endpoint."""

    value: str
    label: str


class EconomicAreaOption(BaseModel):
    """Schema for economic area option in meta endpoint."""

    value: str
    label: str


class CurrencyOption(BaseModel):
    """Schema for currency option in meta endpoint."""

    code: str

    name: str
    digits: int = Field(default=2, description="Decimal precision (exponent)")


class MetaOptionsResponse(BaseModel):
    """Schema for meta options endpoint response."""

    account_types: list[AccountTypeOption]
    economic_areas: list[EconomicAreaOption]
    currencies: list[CurrencyOption]
