from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.config import settings

import backend.models

from backend.routers import auth, products, orders, chat, cart, admin


# Create database tables
# For production later, replace with Alembic migrations
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    description="A modern electronics e-commerce API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS
# Change allow_origins to your frontend URL before final production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"]
)

app.include_router(
    products.router,
    prefix="/api/products",
    tags=["Products"]
)

app.include_router(
    cart.router,
    prefix="/api/cart",
    tags=["Cart"]
)

app.include_router(
    orders.router,
    prefix="/api/orders",
    tags=["Orders"]
)

app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["Admin"]
)

app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["Chat"]
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Nexora API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME
    }
@app.get("/debug/database")
def debug_database():
    from backend.database import DATABASE_URL
    return {
        "database": DATABASE_URL[:50]
    }