from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.auth.router import router as auth_router
from app.bookings.router import router as bookings_router
from app.cleaners.router import router as cleaners_router
from app.admin.router import router as admin_router
from app.websocket.router import router as websocket_router
from app.services.packages_router import router as packages_router

app = FastAPI(
    title="Washioo - On-Demand Vehicle Wash API",
    description="Backend API for vehicle wash booking platform",
    version="1.0.0"
)

# CORS (allow all for MVP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Washioo API is running"}

# Register routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(packages_router, prefix="/packages", tags=["Packages"])
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
app.include_router(cleaners_router, prefix="/cleaner", tags=["Cleaner"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(websocket_router, tags=["WebSocket"])
