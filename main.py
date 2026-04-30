from fastapi import FastAPI
from routers.auth_router import router as auth_router
from routers.services_router import router as services_router
from core.database import Base, engine
from models import user_role, service_category, booking, address

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cash Wash Service Portal Auth API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(services_router)

@app.get("/")
def root():
    return {"message": "Car Wash Auth API Running Successfully"}