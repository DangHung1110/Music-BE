import httpx
from infrastructure.config.jamendo import JamendoConfig
class MusicRespository:
    def __init__(self):
        self.CLIENT_ID=JamendoConfig.CLIENT_ID
        self.BASE_URL=JamendoConfig.BASE_URL
    async def search_tracks(self,query:str,limit:int=10):
        url=f"{self.BASE_URL}/tracks"
        params={
            "client_id":self.CLIENT_ID,
            "format":"json",
            "limit":limit,
            "name":query
        }
        async with httpx.AsyncClient() as client:
            response=await client.get(url,params=params)
            return response.json()