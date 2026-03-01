from fastapi import FastAPI
from app.routers import auth, flights, bookings, admin
from fastapi.middleware.cors import CORSMiddleware
from app.database import client
from app.seed import seed_data

app = FastAPI(
    title="DS Airlines API",
    description="Backend API for DS Airlines, a modern flight booking system.",
    version="2.0.0"
)

# CORS (Cross-Origin Resource Sharing) middleware
app.add_middleware(
    CORSMiddleware,
    # Allow all local origins (including ports) for dev
    allow_origin_regex="https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    # Ping database to verify connection
    try:
        await client.server_info()
        print("Connected to MongoDB")
        await seed_data()
    except Exception as e:
        print(f"Unable to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(flights.router, prefix="/api/flights", tags=["Flights"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to DS Airlines API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
