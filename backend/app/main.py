from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth, restaurants, offers, claims, transactions, loyalty, recommendations, admin

app = FastAPI(
    title=settings.APP_NAME,
    description="Restaurant revenue intelligence + off-peak marketplace (hackathon prototype).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(offers.router)
app.include_router(claims.router)
app.include_router(transactions.router)
app.include_router(loyalty.router)
app.include_router(recommendations.router)
app.include_router(admin.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
