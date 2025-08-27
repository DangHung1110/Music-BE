from fastapi import APIRouter,Query
from shared.responses import OK
from business.services.music_service import MusicService
router=APIRouter(prefix="/music",tags=["Music"])
@router.get( "/search")
async def search_music(query: str = Query(..., description="Search keyword for tracks"),):
    music_service=MusicService()
    results=await music_service.search_tracks(query)
    return OK(message="Tracks fetched successfully",metadata={"tracks":results}).send()
