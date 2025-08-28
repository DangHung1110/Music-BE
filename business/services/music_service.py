from data.repositories.music_repository import MusicRespository

class MusicService:
    def __init__(self):
        self.respo = MusicRespository()

    async def search_tracks(self, query: str):
        tracks = await self.respo.search_tracks(query)
        results = []
        for track in tracks.get("results", []):
            results.append({
                "jamendo_id": track.get("id"),
                "title": track.get("name"),
                "duration": track.get("duration"),
                "file_url": track.get("audiodownload"),
                "cover_url": track.get("album_image"),
                "artist_id": track.get("artist_id"),
                "audio": track.get("audio")
            })
        return results
