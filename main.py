from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.routes import assets, auth
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: (add cleanup code here if needed)


app = FastAPI(
    title="Airport Asset Management API",
    lifespan=lifespan
)

app.include_router(assets.router)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def read_root():
    return {"message": "Welcome to Airport Asset Management API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "service": "airport-asset-api"}