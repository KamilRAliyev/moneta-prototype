"""Meta service for static option data."""

from server.api.schemas.account import (
    AccountTypeOption,
    CurrencyOption,
    EconomicAreaOption,
    MetaOptionsResponse,
)
from server.models.account import AccountType, Currency, EconomicArea


class MetaService:
    """Service for meta/static data operations."""

    def get_accounts_options(self) -> MetaOptionsResponse:
        """Get all static option data for Accounts UI.

        Returns account types, economic areas, and currencies.
        UI must not hardcode these values.
        """
        # Account types
        account_types = [
            {"value": AccountType.CHECKING.value, "label": "Checking"},
            {"value": AccountType.SAVINGS.value, "label": "Savings"},
            {"value": AccountType.CREDIT_CARD.value, "label": "Credit Card"},
            {"value": AccountType.CASH.value, "label": "Cash"},
            {"value": AccountType.INVESTMENT.value, "label": "Investment"},
            {"value": AccountType.LOAN.value, "label": "Loan"},
        ]

        # Economic areas
        economic_areas = [
            {"value": EconomicArea.EU.value, "label": "European Union"},
            {"value": EconomicArea.US.value, "label": "United States"},
            {"value": EconomicArea.UK.value, "label": "United Kingdom"},
            {
                "value": EconomicArea.CIS.value,
                "label": "Commonwealth of Independent States",
            },
            {"value": EconomicArea.MENA.value, "label": "Middle East and North Africa"},
            {
                "value": EconomicArea.APAC.value,
                "label": "Asia-Pacific (excluding China)",
            },
            {"value": EconomicArea.CHINA.value, "label": "China"},
            {"value": EconomicArea.OTHER.value, "label": "Other regions"},
        ]

        # Currencies - get all from Currency enum
        currencies = []
        for currency_member in Currency:
            try:
                exponent = currency_member.exponent
                if exponent is None:
                    exponent = 2  # Default to 2 decimal places
                currencies.append(
                    {
                        "code": currency_member.value,
                        "name": currency_member.name_full,
                        "digits": exponent,
                    }
                )
            except (AttributeError, TypeError):
                # Fallback if helper methods don't work
                currencies.append(
                    {
                        "code": currency_member.value,
                        "name": currency_member.value,
                        "digits": 2,
                    }
                )

        return MetaOptionsResponse(
            account_types=[AccountTypeOption(**at) for at in account_types],
            economic_areas=[EconomicAreaOption(**ea) for ea in economic_areas],
            currencies=[CurrencyOption(**c) for c in currencies],
        )
