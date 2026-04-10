from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import gdp, commodities, forex, countries, ai_insights
import os

app = FastAPI(title="Trade Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gdp.router,         prefix="/api/gdp",         tags=["GDP"])
app.include_router(commodities.router, prefix="/api/commodities", tags=["Commodities"])
app.include_router(forex.router,       prefix="/api/forex",       tags=["Forex"])
app.include_router(countries.router,   prefix="/api/countries",   tags=["Countries"])
app.include_router(ai_insights.router, prefix="/api/ai/insights", tags=["AI"])

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
