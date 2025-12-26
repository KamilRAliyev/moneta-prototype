"""Tests for Accounts API endpoints."""

from datetime import date
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.models.account import Account, AccountType, Currency, EconomicArea

client = TestClient(app)


def patch_db_session(test_db):
    """Context manager to patch database session for testing."""
    from server.core.database import SessionLocal

    def override_get_db():
        session = test_db()
        try:
            yield session
        finally:
            session.close()

    return patch("server.core.database.SessionLocal", test_db), patch(
        "server.core.database.get_db", override_get_db
    )


def use_test_db(test_db):
    """Context manager that patches both SessionLocal and get_db."""
    patch_session, patch_get_db = patch_db_session(test_db)
    return patch_session, patch_get_db


def test_list_accounts_empty(test_db):
    """Test listing accounts when none exist."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.get("/api/v1/accounts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


def test_list_accounts_with_data(test_db):
    """Test listing accounts with data."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create test accounts in the same session context
        session = test_db()
        try:
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
            session.close()

            response = client.get("/api/v1/accounts")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] in ["Account 1", "Account 2"]
            assert data[1]["name"] in ["Account 1", "Account 2"]
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_list_accounts_pagination(test_db):
    """Test listing accounts with pagination."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create multiple accounts in the same session context
        session = test_db()
        try:
            for i in range(5):
                account = Account(
                    name=f"Account {i}",
                    institution=f"Bank {i}",
                    currency=Currency.USD,
                    type=AccountType.CHECKING,
                )
                session.add(account)
            session.commit()
            session.close()

            # Test with skip and limit
            response = client.get("/api/v1/accounts?skip=2&limit=2")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_get_account_success(test_db):
    """Test getting an account by ID."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account in the same session context
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
            account_id = account.id
            session.close()

            response = client.get(f"/api/v1/accounts/{account_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == account_id
            assert data["name"] == "Test Account"
            assert data["currency"] == "USD"
            assert data["account_type"] == "checking"
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_get_account_not_found(test_db):
    """Test getting a non-existent account."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.get("/api/v1/accounts/99999")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data


def test_create_account_success(test_db):
    """Test creating a new account."""
    account_data = {
        "name": "New Account",
        "institution": "New Bank",
        "currency": "USD",
        "account_type": "checking",
        "economic_area": "us",
        "datelock_from": "2023-01-01",
    }

    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.post("/api/v1/accounts", json=account_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Account"
        assert data["institution"] == "New Bank"
        assert data["currency"] == "USD"
        assert data["account_type"] == "checking"
        assert data["economic_area"] == "us"
        assert data["datelock_from"] == "2023-01-01"
        assert "id" in data
        assert "created_at" in data


def test_create_account_minimal_fields(test_db):
    """Test creating account with only required fields."""
    account_data = {
        "name": "Minimal Account",
        "institution": "Minimal Bank",
        "currency": "EUR",
        "account_type": "savings",
    }

    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.post("/api/v1/accounts", json=account_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Account"
        assert data["economic_area"] is None
        assert data["datelock_from"] is None


def test_create_account_invalid_currency(test_db):
    """Test creating account with invalid currency."""
    account_data = {
        "name": "Test Account",
        "institution": "Test Bank",
        "currency": "INVALID",
        "account_type": "checking",
    }

    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.post("/api/v1/accounts", json=account_data)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data


def test_create_account_invalid_account_type(test_db):
    """Test creating account with invalid account type."""
    account_data = {
        "name": "Test Account",
        "institution": "Test Bank",
        "currency": "USD",
        "account_type": "invalid_type",
    }

    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.post("/api/v1/accounts", json=account_data)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data


def test_create_account_invalid_economic_area(test_db):
    """Test creating account with invalid economic area."""
    account_data = {
        "name": "Test Account",
        "institution": "Test Bank",
        "currency": "USD",
        "account_type": "checking",
        "economic_area": "invalid_area",
    }

    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.post("/api/v1/accounts", json=account_data)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data


def test_update_account_success(test_db):
    """Test updating an account."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account in the same session context
        session = test_db()
        try:
            account = Account(
                name="Original Name",
                institution="Original Bank",
                currency=Currency.USD,
                type=AccountType.CHECKING,
            )
            session.add(account)
            session.commit()
            session.refresh(account)
            account_id = account.id
            session.close()

            update_data = {
                "name": "Updated Name",
                "institution": "Updated Bank",
                "currency": "EUR",
                "account_type": "savings",
            }

            response = client.put(f"/api/v1/accounts/{account_id}", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Name"
            assert data["institution"] == "Updated Bank"
            assert data["currency"] == "EUR"
            assert data["account_type"] == "savings"
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_update_account_partial(test_db):
    """Test partial update of an account."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account in the same session context
        session = test_db()
        try:
            account = Account(
                name="Original Name",
                institution="Original Bank",
                currency=Currency.USD,
                type=AccountType.CHECKING,
            )
            session.add(account)
            session.commit()
            session.refresh(account)
            account_id = account.id
            session.close()

            # Only update name
            update_data = {"name": "Partially Updated"}

            response = client.put(f"/api/v1/accounts/{account_id}", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Partially Updated"
            assert data["institution"] == "Original Bank"  # Unchanged
            assert data["currency"] == "USD"  # Unchanged
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_update_account_not_found(test_db):
    """Test updating a non-existent account."""
    update_data = {"name": "Updated Name"}

    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.put("/api/v1/accounts/99999", json=update_data)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data


def test_delete_account_success(test_db):
    """Test deleting an account."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account in the same session context
        session = test_db()
        try:
            account = Account(
                name="To Delete",
                institution="Delete Bank",
                currency=Currency.USD,
                type=AccountType.CHECKING,
            )
            session.add(account)
            session.commit()
            session.refresh(account)
            account_id = account.id
            session.close()

            response = client.delete(f"/api/v1/accounts/{account_id}")

            assert response.status_code == 204

            # Verify account is deleted
            get_response = client.get(f"/api/v1/accounts/{account_id}")
            assert get_response.status_code == 404
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_delete_account_not_found(test_db):
    """Test deleting a non-existent account."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.delete("/api/v1/accounts/99999")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data


def test_meta_accounts_options():
    """Test meta accounts options endpoint."""
    response = client.get("/api/v1/meta/accounts/options")

    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "account_types" in data
    assert "economic_areas" in data
    assert "currencies" in data

    # Check account_types
    account_types = data["account_types"]
    assert isinstance(account_types, list)
    assert len(account_types) > 0
    assert all("value" in at and "label" in at for at in account_types)

    # Check economic_areas
    economic_areas = data["economic_areas"]
    assert isinstance(economic_areas, list)
    assert len(economic_areas) > 0
    assert all("value" in ea and "label" in ea for ea in economic_areas)

    # Check currencies
    currencies = data["currencies"]
    assert isinstance(currencies, list)
    assert len(currencies) > 0
    assert all("code" in c and "name" in c and "digits" in c for c in currencies)

    # Verify specific values
    account_type_values = [at["value"] for at in account_types]
    assert "checking" in account_type_values
    assert "savings" in account_type_values

    currency_codes = [c["code"] for c in currencies]
    assert "USD" in currency_codes
    assert "EUR" in currency_codes
