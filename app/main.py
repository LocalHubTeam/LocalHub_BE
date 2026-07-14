from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .seed import seed_all
from .routers.posts import router as posts_router
from .routers import location

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://localhub-frontend.netlify.app",
        "*",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router)
app.include_router(location.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_all()

@app.get("/")
def health_check():
    return {"status": "ok"}