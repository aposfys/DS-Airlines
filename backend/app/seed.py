from app.database import db
from datetime import datetime, timedelta
import bcrypt

async def seed_data():
    # Seed admin user if it doesn't exist
    admin_user = await db.users.find_one({"username": "admin@unipi.gr"})
    if not admin_user:
        print("Seeding default admin user...")
        password = "admin"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        await db.users.insert_one({
            "fullname": "Administrator",
            "username": "admin@unipi.gr",
            "email": "admin@unipi.gr",
            "password": hashed_password,
            "passport_num": "ADMIN001",
            "is_admin": True
        })

    # Seed some sample flights if none exist
    flights_count = await db.availableFlights.count_documents({})
    if flights_count == 0:
        print("Seeding sample flights...")
        today = datetime.now()
        flights = [
            {
                "unique_code": "AEE123",
                "departure": "Athens (ATH)",
                "destination": "London (LHR)",
                "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "10:30",
                "cost": 185.50
            },
            {
                "unique_code": "AEE456",
                "departure": "Thessaloniki (SKG)",
                "destination": "Frankfurt (FRA)",
                "date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
                "time": "14:15",
                "cost": 210.00
            },
            {
                "unique_code": "AEE789",
                "departure": "Athens (ATH)",
                "destination": "Paris (CDG)",
                "date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
                "time": "08:45",
                "cost": 150.75
            }
        ]
        await db.availableFlights.insert_many(flights)
        print(f"Seeded {len(flights)} flights.")
