"""Meta endpoints for static option data."""

from fastapi import APIRouter

from server.api.schemas.account import MetaOptionsResponse
from server.services.meta import MetaService

router = APIRouter(prefix="/meta", tags=["Meta"])


@router.get("/accounts/options", response_model=MetaOptionsResponse)
def get_accounts_options() -> MetaOptionsResponse:
    """Get all static option data for Accounts UI.

    Returns account types, economic areas, and currencies.
    UI must not hardcode these values.
    """
    service = MetaService()
    return service.get_accounts_options()
