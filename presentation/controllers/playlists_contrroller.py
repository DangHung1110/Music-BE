from fastapi import APIRouter,Query
from shared.responses import OK
from business.services.playlists_service import PlayListService
router=APIRouter(prefix="/Playlist",tags=["Playlist"])
@router.get("/search")
async def search_music(query: str = Query(..., description="Search keyword for tracks"),):
    playlist_service=PlayListService()
    results=await playlist_service.search_playlist(query)
    return OK(message="Tracks fetched successfully",metadata={"playlists":results}).send()