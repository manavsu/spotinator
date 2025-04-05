from fastapi import APIRouter
from routes.user_routes import router as user_routes
from routes.spotify_routes import router as spotify_routes

router = APIRouter()
router.include_router(spotify_routes)
