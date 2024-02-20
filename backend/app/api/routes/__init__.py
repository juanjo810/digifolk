from fastapi import APIRouter
from app.api.routes import user_route, col_route, piece_route, items_route

router = APIRouter()

router.include_router(user_route.router, tags=["user"])
router.include_router(piece_route.router, tags=["piece"])
router.include_router(col_route.router, tags=["collection"])
router.include_router(items_route.router, tags=["items"])


@router.get("/")
async def main():
    return [{"msg": "main"}]
