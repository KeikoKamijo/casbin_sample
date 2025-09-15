from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import users, corporations, schools, inquiries

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="PyCasbin Sample API",
    description="PyCasbinを使用したRBACサンプルAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(corporations.router)
app.include_router(schools.router)
app.include_router(inquiries.router)


@app.get("/", tags=["health"], summary="ヘルスチェック")
async def root():
    """
    APIヘルスチェックエンドポイント
    """
    return {
        "message": "PyCasbin Sample API",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"], summary="詳細ヘルスチェック")
async def health_check():
    """
    詳細なヘルスチェック情報を返します
    """
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0",
        "endpoints": {
            "users": "/api/v1/users",
            "corporations": "/api/v1/corporations",
            "schools": "/api/v1/schools",
            "inquiries": "/api/v1/inquiries"
        }
    }