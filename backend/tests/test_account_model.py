"""Tests for Account model."""

from datetime import date

import pytest

from server.models.account import Account, AccountType, Currency, EconomicArea


def test_account_model_creation(test_db):
    """Test creating an Account model instance."""
    session = test_db()

    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )

        session.add(account)
        session.commit()
        session.refresh(account)

        assert account.id is not None
        assert account.name == "Test Account"
        assert account.institution == "Test Bank"
        assert account.currency == Currency.USD
        assert account.type == AccountType.CHECKING
        assert account.economic_area is None
        assert account.datelock_from is None
        assert account.created_at is not None
    finally:
        session.close()


def test_account_model_with_all_fields(test_db):
    """Test Account model with all fields populated."""
    session = test_db()

    try:
        account = Account(
            name="Savings Account",
            institution="Bank of Test",
            currency=Currency.EUR,
            type=AccountType.SAVINGS,
            economic_area=EconomicArea.EU,
            datelock_from=date(2023, 1, 1),
        )

        session.add(account)
        session.commit()
        session.refresh(account)

        assert account.name == "Savings Account"
        assert account.institution == "Bank of Test"
        assert account.currency == Currency.EUR
        assert account.type == AccountType.SAVINGS
        assert account.economic_area == EconomicArea.EU
        assert account.datelock_from == date(2023, 1, 1)
        assert account.datelock_to is None
        assert account.created_at is not None
    finally:
        session.close()


def test_account_model_with_datelock_to(test_db):
    """Test Account model with datelock_to field."""
    session = test_db()

    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2023, 1, 1),
            datelock_to=date(2023, 12, 31),
        )

        session.add(account)
        session.commit()
        session.refresh(account)

        assert account.datelock_from == date(2023, 1, 1)
        assert account.datelock_to == date(2023, 12, 31)
    finally:
        session.close()


def test_account_model_datelock_to_nullable(test_db):
    """Test that datelock_to can be None."""
    session = test_db()

    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2023, 1, 1),
            datelock_to=None,
        )

        session.add(account)
        session.commit()
        session.refresh(account)

        assert account.datelock_from == date(2023, 1, 1)
        assert account.datelock_to is None
    finally:
        session.close()


def test_account_model_timestamps(test_db):
    """Test that Account model has automatic timestamps."""
    session = test_db()

    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.GBP,
            type=AccountType.CHECKING,
        )

        session.add(account)
        session.commit()
        session.refresh(account)

        assert account.created_at is not None
        # updated_at should be None initially
        assert account.updated_at is None

        # Update account
        account.name = "Updated Account"
        session.commit()
        session.refresh(account)

        # updated_at should be set after update
        assert account.updated_at is not None
    finally:
        session.close()


def test_account_type_enum():
    """Test AccountType enum values."""
    assert AccountType.CHECKING.value == "checking"
    assert AccountType.SAVINGS.value == "savings"
    assert AccountType.CREDIT_CARD.value == "credit_card"
    assert AccountType.CASH.value == "cash"
    assert AccountType.INVESTMENT.value == "investment"
    assert AccountType.LOAN.value == "loan"


def test_economic_area_enum():
    """Test EconomicArea enum values and descriptions."""
    assert EconomicArea.EU.value == "eu"
    assert EconomicArea.US.value == "us"
    assert EconomicArea.UK.value == "uk"
    assert EconomicArea.CIS.value == "cis"
    assert EconomicArea.MENA.value == "mena"
    assert EconomicArea.APAC.value == "apac"
    assert EconomicArea.CHINA.value == "china"
    assert EconomicArea.OTHER.value == "other"

    # Test description helper
    assert EconomicArea.EU.description == "European Union"
    assert EconomicArea.US.description == "United States"


def test_currency_enum():
    """Test Currency enum from ISO 4217."""
    # Test that common currencies exist
    assert Currency.USD.value == "USD"
    assert Currency.EUR.value == "EUR"
    assert Currency.GBP.value == "GBP"
    assert Currency.JPY.value == "JPY"

    # Test helper methods
    assert Currency.USD.name_full == "US Dollar"
    assert Currency.EUR.name_full == "Euro"
    assert Currency.USD.exponent == 2
    assert Currency.JPY.exponent == 0  # Japanese Yen has no decimal places


def test_currency_enum_lookup():
    """Test Currency enum lookup by string."""
    # Test _missing_ method
    usd = Currency("USD")
    assert usd == Currency.USD

    eur = Currency("eur")  # Should work with lowercase
    assert eur == Currency.EUR


def test_account_query(test_db):
    """Test querying accounts from database."""
    session = test_db()

    try:
        # Create multiple accounts
        account1 = Account(
            name="Account 1",
            institution="Bank 1",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        account2 = Account(
            name="Account 2",
            institution="Bank 2",
            currency=Currency.EUR,
            type=AccountType.SAVINGS,
        )

        session.add_all([account1, account2])
        session.commit()

        # Query all accounts
        accounts = session.query(Account).all()
        assert len(accounts) == 2

        # Query by ID
        found_account = session.query(Account).filter(Account.id == account1.id).first()
        assert found_account is not None
        assert found_account.name == "Account 1"

        # Query by currency
        usd_accounts = (
            session.query(Account).filter(Account.currency == Currency.USD).all()
        )
        assert len(usd_accounts) == 1
        assert usd_accounts[0].name == "Account 1"
    finally:
        session.close()
