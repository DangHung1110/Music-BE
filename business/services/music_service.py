from data.repositories.music_repository import MusicRespository
class MusicService:
    def __init__(self):
        self.respo=MusicRespository()
    async def search_tracks(self,query:str):
        data=await self.respo.search_tracks(query)
        return [
            {
                "name":track["name"]
            }
        ]
    