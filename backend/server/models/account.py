"""Account model."""

import enum

from iso4217 import Currency as ISO4217Currency
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.sql import func
from server.models import Base


class AccountType(enum.Enum):
    """Account type enumeration."""

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    INVESTMENT = "investment"
    LOAN = "loan"


# Collect all currency codes from iso4217 to create enum
_currency_members = {}
for attr_name in dir(ISO4217Currency):
    if not attr_name.startswith("_") and attr_name.isupper():
        try:
            currency_obj = getattr(ISO4217Currency, attr_name)
            if hasattr(currency_obj, "code") and hasattr(currency_obj, "currency_name"):
                _currency_members[attr_name] = currency_obj.code
        except (AttributeError, TypeError):
            continue


# Create Currency enum using functional API
Currency = enum.Enum("Currency", _currency_members, type=str)


# Add helper methods to Currency enum
def _name_full(self) -> str:
    """Get human-readable currency name from ISO 4217."""
    try:
        currency_obj = getattr(ISO4217Currency, self.name)
        return currency_obj.currency_name
    except AttributeError:
        return "Unknown Currency"


def _exponent(self) -> int:
    """Get decimal exponent (number of decimal places) from ISO 4217."""
    try:
        currency_obj = getattr(ISO4217Currency, self.name)
        return currency_obj.exponent
    except AttributeError:
        return 2  # Default to 2 decimal places


def _missing_(cls, value):
    """Allow lookup by currency code string."""
    if isinstance(value, str):
        for member in cls:
            if member.value == value.upper():
                return member
    return None


# Attach helper methods and _missing_ to the enum class
Currency.name_full = property(_name_full)
Currency.exponent = property(_exponent)
Currency._missing_ = classmethod(_missing_)


class EconomicArea(enum.Enum):
    """Economic area enumeration with regional classifications."""

    EU = "eu"
    US = "us"
    UK = "uk"
    CIS = "cis"
    MENA = "mena"
    APAC = "apac"
    CHINA = "china"
    OTHER = "other"

    @classmethod
    def get_description(cls, value: "EconomicArea") -> str:
        """Get human-readable description for an economic area."""
        descriptions = {
            cls.EU: "European Union",
            cls.US: "United States",
            cls.UK: "United Kingdom",
            cls.CIS: "Commonwealth of Independent States",
            cls.MENA: "Middle East and North Africa",
            cls.APAC: "Asia-Pacific (excluding China)",
            cls.CHINA: "China",
            cls.OTHER: "Other regions",
        }
        return descriptions.get(value, "Unknown")

    @property
    def description(self) -> str:
        """Get human-readable description for this economic area."""
        return self.get_description(self)


class Account(Base):
    """Account model for managing financial accounts."""

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    currency = Column(Enum(Currency, native_enum=False), nullable=False)
    type = Column(Enum(AccountType, native_enum=False), nullable=False)
    economic_area = Column(Enum(EconomicArea, native_enum=False), nullable=True)
    datelock_from = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
