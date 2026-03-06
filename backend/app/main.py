from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import engine, Base, SessionLocal
from app.routers import item_router, user_router, favorite_router, order_router, chat_router, ml_router
from app.utils.seed_data import seed_items

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Shopping Website API",
    description="A full end-to-end shopping website with AI capabilities",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(item_router.router, prefix="/api")
app.include_router(user_router.router, prefix="/api")
app.include_router(favorite_router.router, prefix="/api")
app.include_router(order_router.router, prefix="/api")
app.include_router(chat_router.router, prefix="/api")
app.include_router(ml_router.router, prefix="/api")


@app.on_event("startup")
def startup_event():
    """Seed the database with initial data on startup."""
    db = SessionLocal()
    try:
        seed_items(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Welcome to the AI Shopping Website API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
