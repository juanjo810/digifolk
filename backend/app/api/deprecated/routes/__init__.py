from fastapi import APIRouter

from app.api.routes.platform import search, music, models, games, user, gallery

from app.api.routes.admin import music as admin_music
from app.api.routes.admin import levels as admin_music_levels
from app.api.routes.admin import search as admin_search
from app.api.routes.admin import models as admin_models
from app.api.routes.admin import lyrics as admin_lyrics
from app.api.routes.admin import dance_steps as admin_dance
from app.api.routes.admin import users as admin_users

router = APIRouter()

# Admin Routers
router.include_router(admin_music.router, tags=["admin_music"])
router.include_router(admin_music_levels.router, tags=["admin_music_levels"])
router.include_router(admin_search.router, tags=["admin_search"])
router.include_router(admin_models.router, tags=["admin_models"])
router.include_router(admin_lyrics.router, tags=["admin_lyrics"])
router.include_router(admin_dance.router, tags=["admin_dance"])
router.include_router(admin_users.router, tags=["admin_users"])

# Platform Routers
router.include_router(music.router, tags=["music"])
router.include_router(search.router, tags=["search"])
router.include_router(models.router, tags=["models"])
router.include_router(games.router, tags=["games"])
router.include_router(user.router, tags=["users"])
router.include_router(gallery.router, tags=["gallery"])


@router.get("/")
async def main():
    return [{"msg": "main"}]
