from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from presentation.middleware.error_middleware import ErrorHandlerMiddleware
from infrastructure.config.redis import close_redis, get_redis

load_dotenv()

# Import auth router
from presentation.controllers.auth_controller import router as auth_router
from presentation.controllers.music_controller import router as music_router
from presentation.controllers.playlists_contrroller import router as playlist_router
app = FastAPI(
    title="Music Streaming API",
    description="A modern music streaming backend built with FastAPI",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc"       # ReDoc
)

app.add_middleware(ErrorHandlerMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(music_router,prefix="/api/v1", tags=["Music"])
app.include_router(playlist_router, prefix="/api/v1", tags=["Playlist"])

# Add Redis startup/shutdown events
@app.on_event("startup")
async def startup_event():
    await get_redis()
    print("Redis connection established")

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()
    print("Redis connection closed")
@app.get("/")
async def root():
    return {
        "message": "Music Streaming API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        log_level="info"
    )
