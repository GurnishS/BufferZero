from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.admin import router as admin_router
from app.routes.youtube import router as youtube_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the BufferZero!"}

app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(youtube_router, prefix="/api/yt", tags=["youtube"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)