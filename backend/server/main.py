from fastapi import FastAPI, APIRouter
from server.core import settings
from server.services import health

app = FastAPI(title="Moneta API", version="0.1.0")

router = APIRouter(prefix="/api")


@router.get("/health", tags=["Health"])
def health_check():
    return health.get_health_info()


app.include_router(router)
