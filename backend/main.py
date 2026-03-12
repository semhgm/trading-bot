from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from auth import create_default_user
import uvicorn

app = FastAPI(title="Trading Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://54.209.228.76"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Uygulama başlarken default user oluştur
create_default_user()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
