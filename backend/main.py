from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.config import settings
import backend.models
from backend.routers import auth, products, orders, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="A modern electronics e-commerce API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# TODO: Restrict allow_origins to your deployed frontend URL(s) before production
# (e.g. ["https://nexora.example.com"]). Using "*" is fine for local dev only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router,   prefix="/api/orders",   tags=["Orders"])
app.include_router(chat.router,     prefix="/api/chat",     tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Welcome to Nexora API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}